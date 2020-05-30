#pragma once

namespace poly::structures {

    class ViewPlane {
    public:
        ViewPlane() = default;
        int hres;
        int vres;
        int gamma;
        unsigned int max_depth;
    };
}