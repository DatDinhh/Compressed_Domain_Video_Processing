#pragma once
#include <string>
#include <vector>

namespace cdproc {

struct Feat {
    double t;  
    double E;   
    double S;   
    double div; 
};

std::vector<Feat> extract_features_mv(const std::string& path, bool average=true);

}
