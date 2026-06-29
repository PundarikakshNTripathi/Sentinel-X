#include <emscripten.h>
#include <string>
#include <cmath>
#include <unordered_map>

extern "C" {

EMSCRIPTEN_KEEPALIVE
double calculate_entropy(const char* str) {
    if (!str) return 0.0;
    
    std::string s(str);
    if (s.empty()) return 0.0;
    
    std::unordered_map<char, int> frequencies;
    for (char c : s) {
        frequencies[c]++;
    }
    
    double entropy = 0.0;
    double len = static_cast<double>(s.length());
    
    for (auto const& [key, val] : frequencies) {
        double p = val / len;
        entropy -= p * std::log2(p);
    }
    
    return entropy;
}

}
