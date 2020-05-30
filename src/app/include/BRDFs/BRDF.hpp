#pragma once


namespace poly::material {

    class BRDF {
    public:
        BRDF() = default;
        virtual Colour f(poly::structures::ShadeRec const& sr,
                         atlas::math::Vector& w_o,
                         atlas::math::Vector& w_i) const = 0;
        virtual Colour rho(poly::structures::ShadeRec const& sr,
                           atlas::math::Vector& w_o) const = 0;
    };
}