#include "include/cdproc_mv.hpp"
#include <stdexcept>
#include <vector>
#include <cmath>
extern "C" {
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavutil/motion_vector.h>
}

namespace cdproc {

static double safe_time(const AVFrame* f, const AVStream* st, int64_t frame_idx) {
    if (f->best_effort_timestamp != AV_NOPTS_VALUE) {
        return f->best_effort_timestamp * av_q2d(st->time_base);
    }
    // fallback: use avg_frame_rate (or r_frame_rate) to synthesize a timestamp
    AVRational r = st->avg_frame_rate.num ? st->avg_frame_rate : st->r_frame_rate;
    double fps = (r.num && r.den) ? av_q2d(r) : 30.0;
    return frame_idx / (fps > 0 ? fps : 30.0);
}

std::vector<Feat> extract_features_mv(const std::string& path, bool average) {
    std::vector<Feat> out;

    AVFormatContext* fmt = nullptr;
    if (avformat_open_input(&fmt, path.c_str(), nullptr, nullptr) < 0) {
        throw std::runtime_error("avformat_open_input failed");
    }
    if (avformat_find_stream_info(fmt, nullptr) < 0) {
        avformat_close_input(&fmt);
        throw std::runtime_error("avformat_find_stream_info failed");
    }

    // find first video stream
    int vidx = av_find_best_stream(fmt, AVMEDIA_TYPE_VIDEO, -1, -1, nullptr, 0);
    if (vidx < 0) {
        avformat_close_input(&fmt);
        throw std::runtime_error("no video stream");
    }
    AVStream* vs = fmt->streams[vidx];

    const AVCodec* dec = avcodec_find_decoder(vs->codecpar->codec_id);
    if (!dec) { avformat_close_input(&fmt); throw std::runtime_error("decoder not found"); }

    AVCodecContext* ctx = avcodec_alloc_context3(dec);
    if (!ctx) { avformat_close_input(&fmt); throw std::runtime_error("alloc ctx failed"); }
    if (avcodec_parameters_to_context(ctx, vs->codecpar) < 0) {
        avcodec_free_context(&ctx); avformat_close_input(&fmt);
        throw std::runtime_error("parameters_to_context failed");
    }

    // CRUCIAL: ask decoder to export motion vectors
    ctx->flags2 |= AV_CODEC_FLAG2_EXPORT_MVS;

    if (avcodec_open2(ctx, dec, nullptr) < 0) {
        avcodec_free_context(&ctx); avformat_close_input(&fmt);
        throw std::runtime_error("avcodec_open2 failed");
    }

    AVPacket* pkt = av_packet_alloc();
    AVFrame*  frm = av_frame_alloc();
    if (!pkt || !frm) { /* clean up */ }

    int64_t frame_idx = 0;
    while (av_read_frame(fmt, pkt) >= 0) {
        if (pkt->stream_index != vidx) { av_packet_unref(pkt); continue; }
        if (avcodec_send_packet(ctx, pkt) < 0) { av_packet_unref(pkt); break; }
        av_packet_unref(pkt);

        while (true) {
            int ret = avcodec_receive_frame(ctx, frm);
            if (ret == AVERROR(EAGAIN) || ret == AVERROR_EOF) break;
            if (ret < 0) { break; }

            // gather motion vectors from side data
            const AVFrameSideData* sd = av_frame_get_side_data(frm, AV_FRAME_DATA_MOTION_VECTORS);
            double esum = 0.0, ssum = 0.0, dsum = 0.0; // E, S, div accumulators
            int count = 0;

            if (sd && sd->data && sd->size >= sizeof(AVMotionVector)) {
                auto* mvs = reinterpret_cast<const AVMotionVector*>(sd->data);
                int nmv = sd->size / sizeof(AVMotionVector);
                for (int i = 0; i < nmv; ++i) {
                    const auto& mv = mvs[i];
                    // pixel motion (dx, dy) is in quarter-pel for some codecs; FFmpeg reports in pixels for MV side data.
                    double dx = static_cast<double>(mv.motion_x);
                    double dy = static_cast<double>(mv.motion_y);
                    double sp2 = dx*dx + dy*dy;     // squared speed
                    double sp1 = std::abs(dx) + std::abs(dy); // L1 speed
                    esum += sp2;
                    ssum += sp1;
                    // very cheap “divergence”: sign of forward/backward differences by ref
                    dsum += (mv.source == 0 ? 1.0 : -1.0) * sp1;
                    ++count;
                }
            }

            Feat f{};
            f.t   = safe_time(frm, vs, frame_idx++);
            if (count > 0) {
                if (average) {
                    f.E = esum / count;
                    f.S = ssum / count;
                    f.div = dsum / count;
                } else {
                    f.E = esum; f.S = ssum; f.div = dsum;
                }
            } else {
                f.E = 0.0; f.S = 0.0; f.div = 0.0;
            }
            out.emplace_back(f);

            av_frame_unref(frm);
        }
    }

    // flush
    avcodec_send_packet(ctx, nullptr);
    while (avcodec_receive_frame(ctx, frm) == 0) {
        Feat f{};
        f.t = safe_time(frm, vs, frame_idx++);
        out.emplace_back(f);
        av_frame_unref(frm);
    }

    av_frame_free(&frm);
    av_packet_free(&pkt);
    avcodec_free_context(&ctx);
    avformat_close_input(&fmt);
    return out;
}

} 
