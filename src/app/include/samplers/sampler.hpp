#pragma once

#include <vector>

namespace poly::sampler {

    class Sampler {
    public:
        unsigned int granularity = 5000;

        Sampler() {
          count = 0;
          num_samples = 1;
          num_sets = 1;
        }
        ~Sampler() {}

        unsigned int num_samples_get() { return num_samples * num_sets; }
        virtual void generate_samples() = 0;
        virtual std::vector<float> sample_unit_square() = 0;
        virtual std::vector<float> sample_unit_square(const unsigned int) = 0;
        virtual std::vector<float> sample_hemisphere() = 0;
        virtual std::vector<float> sample_hemisphere(const unsigned int) = 0;
        virtual void map_samples_to_hemisphere(const float e) = 0;

    protected:
        unsigned int num_samples;
        unsigned int num_sets;
        unsigned int count;
        std::vector<std::vector<float>> samples;
        std::vector<std::vector<float>> hemisphere_samples;
    };
}