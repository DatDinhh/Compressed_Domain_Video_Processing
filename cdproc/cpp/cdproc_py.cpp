#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "include/cdproc_mv.hpp"

namespace py = pybind11;

PYBIND11_MODULE(cdproc_cpp, m) {
    m.doc() = "cdproc C++ motion-vector extractor";

    m.def("extract_features",
          [](const std::string& path, bool average) {
              std::vector<cdproc::Feat> feats = cdproc::extract_features_mv(path, average);

              py::list out;
              for (const auto& f : feats) {
                  py::dict d;
                  d["t"]   = f.t;   
                  d["E"]   = f.E;
                  d["S"]   = f.S;
                  d["div"] = f.div;
                  out.append(std::move(d));
              }
              return out;
          },
          py::arg("path"),
          py::arg("average") = true);
}
