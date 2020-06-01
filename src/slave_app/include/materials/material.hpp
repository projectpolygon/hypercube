#pragma once

#include <structures/shade_rec.hpp>

namespace poly::material {

    class Material {
    public:
        Material() = default;
        virtual Colour shade(poly::structures::ShadeRec& sr) const = 0;
    };
}
