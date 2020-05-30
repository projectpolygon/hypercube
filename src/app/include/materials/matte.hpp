#pragma once

#include <memory>

#include <lights/light.hpp>
#include <BRDFs/lambertian.hpp>

namespace poly::material {

    class Matte : public Material {
    public:
        Matte() {
          m_diffuse = std::make_shared<LambertianBRDF>(
            1.0f,
            random_colour_generate());
        }
        Matte(float f, Colour const& c)
        {
          m_diffuse = std::make_shared<LambertianBRDF>(f, c);
        }

    protected:

        std::shared_ptr<LambertianBRDF> m_diffuse;

        Colour shade(poly::structures::ShadeRec& sr) const {
          // Render loop
          Colour r = Colour(0.0f, 0.0f, 0.0f);
          Colour a;
          atlas::math::Vector nullVec(0.0f, 0.0f, 0.0f);

          if (sr.m_world.m_ambient) {
            a = m_diffuse->rho(sr, nullVec)
                * sr.m_world.m_ambient->L(sr);
          }

          for (std::shared_ptr<poly::light::Light> light : sr.m_world.m_lights) {
            Colour brdf = m_diffuse->f(sr, nullVec, nullVec);
            Colour L = light->L(sr);
            float angle = glm::dot(sr.m_normal,
                                   light->direction_get(sr));
            if (angle > 0) {
              r += (brdf
                    * L
                    * angle);
            }
            else {
              r += Colour(0.0f, 0.0f, 0.0f);
            }
          }

          return (a + r);
        }
    };

}