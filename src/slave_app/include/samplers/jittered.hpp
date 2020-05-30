#pragma once

namespace poly::sampler  {

    class AA_Jittered : public Sampler
    {
    public:

        AA_Jittered()
        {
          generate_samples();
        }

        AA_Jittered(unsigned int num_samp, unsigned int num_set)
        {
          num_samples = num_samp;
          num_sets = num_set;
          generate_samples();
        }

        void generate_samples()
        {
          unsigned int n = (int)sqrt(num_samples);

          // Ensure we're using a perfect square
          assert(n * n == num_samples);

          for (unsigned int set = 0; set < num_sets; set++) {
            for (unsigned int j = 0; j < n; j++) {
              for (unsigned int i = 0; i < n; i++) {
                float new_x = ((float)j
                               + ((float)(rand() % granularity))
                                 / ((float)granularity))
                              / (float)n;
                float new_y = ((float)i
                               + ((float)(rand() % granularity))
                                 / ((float)granularity))
                              / (float)n;
                std::vector<float> sample = { new_x, new_y };
                samples.push_back(sample);
              }
            }
          }
        }

        std::vector<float> sample_unit_square()
        {
          count = ((count + 1) % (num_samples * num_sets));
          return samples.at(count);
        }

        std::vector<float> sample_unit_square(const unsigned int index)
        {
          return samples.at(index % (num_samples * num_sets));
        }

        std::vector<float> sample_hemisphere()
        {
          count = ((count + 1) % (num_samples * num_sets));
          return hemisphere_samples.at(count);
        }

        std::vector<float> sample_hemisphere(const unsigned int index)
        {
          // Ensures that we are only reading (for multithreading)
          return hemisphere_samples.at(index % (num_samples * num_sets));
        }

        void map_samples_to_hemisphere(const float e)
        {
          int size = (int)samples.size();
          hemisphere_samples.reserve(num_samples * (size_t)num_sets);
          for (int i = 0; i < size; i++) {
            float cos_phi = (float)cos(2.0f * (float)glm::pi<float>() * samples.at(i).at(0));
            float sin_phi = (float)sin(2.0f * (float)glm::pi<float>() * samples.at(i).at(0));
            float cos_theta = (float)pow((float)(1.0f - samples.at(i).at(1)),
                                         (float)(1.0f / (e + 1.0f)));
            float sin_theta = (float)sqrt(1.0f - (cos_theta * (float)cos_theta));
            float pu = sin_theta * cos_phi;
            float pv = sin_theta * sin_phi;
            float pw = cos_theta;

            hemisphere_samples.push_back(std::vector<float>{pu, pv, pw});
          }
        }

    };
}