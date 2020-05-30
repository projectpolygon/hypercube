#include <nlohmann/json.hpp>
#include <iostream>
#include <fstream>

#include "structures/world.hpp"

namespace poly::utils {

		math::Vector parse_vector(nlohmann::json vector_json)
		{
			math::Vector v{};
			for (int i = 0; i < 3; ++i) {
				v[i] = vector_json[i];
			}
			return v;
		}

		std::shared_ptr<poly::material::Material> parse_material(nlohmann::json material_json)
		{
			auto material_type = material_json["type"];
			if (material_type == "matte") {
				return std::make_shared<poly::material::Matte>(
					material_json["diffuse"], Colour{parse_vector(material_json["colour"])});
			} else {
				throw std::runtime_error("incorrect material parameters");
			}
		}

		nlohmann::json open_json_file(const char* handle)
		{
			try {
				std::ifstream fs;
				std::string line, json_string;
				fs.open(handle, std::fstream::in);

				while (fs >> line) {
					json_string += line;
				}

				fs.close();
				return nlohmann::json::parse(json_string);

			} catch (std::runtime_error& error) {
				std::cout << error.what() << std::endl;
				return nlohmann::json({});
			}
		}

		poly::structures::World create_world(nlohmann::json& task)
		{
			poly::structures::World w;

			std::shared_ptr<poly::structures::ViewPlane> vp = std::make_shared<poly::structures::ViewPlane>();
			vp->vres = task["job_y"];
			vp->hres = task["job_x"];
			vp->max_depth = task["max_depth"];

			w.m_vp = vp;
			w.m_tracer = std::make_shared<poly::structures::WhittedTracer>(&w);
			w.m_scene = std::vector<std::shared_ptr<poly::object::Object>>();
			w.m_start_width = task["task_startx"];
			w.m_start_height = task["task_starty"];
			w.m_end_width = task["task_endx"];
			w.m_end_height = task["task_endy"];
			w.m_slab_size = (w.m_end_width - w.m_start_width) / (unsigned int)task["threads"];

			try {
				w.m_background = Colour{task["background"]};
			} catch (nlohmann::detail::type_error&  e) {
				w.m_background = {0.0f, 0.0f, 0.0f};
			}

			try {
				auto cam_type = task["camera"]["sampler"]["type"];

				if (cam_type == "jittered") {
					w.m_sampler = std::make_shared<poly::sampler::AA_Jittered>(
						task["camera"]["sampler"]["samples"], task["camera"]["sampler"]["sets"]);
				} else {
					throw std::runtime_error("Incorrect sampler parameters");
				}
			} catch (nlohmann::detail::type_error& e) {
				throw e;
			}

			for (auto obj : task["objects"]) {
				if (obj["type"] == "sphere") {
					std::shared_ptr<poly::object::Sphere> s =
						std::make_shared<poly::object::Sphere>(parse_vector(obj["centre"]), obj["radius"]);

					std::shared_ptr<poly::material::Material> material = parse_material(obj["material"]);
					s->material_set(material);
					w.m_scene.push_back(s);

				}
			}

			for (auto light : task["lights"]) {
				std::shared_ptr<poly::light::Light> l;
				if (light["type"] == "point") {
					l = std::make_shared<poly::light::PointLight>(parse_vector(light["position"]));
					l->radiance_scale(light["intensity"]);
					w.m_lights.push_back(l);
				} else if (light["type"] == "ambient"){
					l = std::make_shared<poly::light::AmbientLight>();
					l->colour_set(parse_vector(light["colour"]));
					l->radiance_scale(light["intensity"]);
					w.m_ambient = l;
				}

			}

			return w;
		}

		poly::camera::PinholeCamera parse_camera(nlohmann::json camera_json)
		{
			poly::camera::PinholeCamera cam = poly::camera::PinholeCamera(camera_json["distance"]);
			cam.eye_set(parse_vector(camera_json["eye"]));
			cam.lookat_set(parse_vector(camera_json["lookat"]));
			cam.upvec_set(parse_vector(camera_json["up"]));
			cam.uvw_compute();
			return cam;
		}
}