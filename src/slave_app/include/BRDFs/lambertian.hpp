#pragma once

#include "BRDF.hpp"


namespace poly::material {

    class LambertianBRDF : public BRDF {
    public:
        LambertianBRDF()
        {
          m_kd = 1.0f;
          m_cd = random_colour_generate();
        }

        LambertianBRDF(const float kd, Colour const& colour)
        {
          m_kd = kd;
          m_cd = colour;
        }

        Colour f([[maybe_unused]] poly::structures::ShadeRec const& sr,
                 [[maybe_unused]] atlas::math::Vector& w_o,
                 [[maybe_unused]] atlas::math::Vector& w_i) const
        {
          return m_kd * m_cd * glm::one_over_pi<float>();
        }

        Colour rho([[maybe_unused]] poly::structures::ShadeRec const& sr,
                   [[maybe_unused]] atlas::math::Vector& w_o) const
        {
          return (Colour)(m_cd * m_kd);
        }

    protected:
        float m_kd;
        Colour m_cd;
    };

}
