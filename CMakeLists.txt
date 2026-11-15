cmake_minimum_required(VERSION 3.8)
project(roboracer_vehicle_model NONE)

find_package(ament_cmake REQUIRED)

# Data-only package: no compilation, just the exported Collada meshes.
#
# The `dae` directory keeps its name under share/${PROJECT_NAME}, so mesh URIs
# stay the same as in a source checkout:
#
#   package://roboracer_vehicle_model/dae/roboracer_frame.dae
#
# New `.dae` files added by tools/export_all.sh are installed automatically.
install(
  DIRECTORY dae
  DESTINATION share/${PROJECT_NAME}
  FILES_MATCHING PATTERN "*.dae"
)

# Keep the licence and the model description with the installed package.
install(
  FILES README.md LICENSE
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
