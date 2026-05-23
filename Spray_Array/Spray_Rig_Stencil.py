from math import *
from solid2 import *
import toml
import subprocess

""" Drill stencil for attaching Spray_Array lid fasteners through a bucket lid.

    Generates a single arc segment (matching the Spray_Rig segments) with holes
    at the exact positions where the pagoda cone fasteners pass through.
    Print one segment, then rotate it around the lid to mark/drill all holes.
"""


def stencil(
    initial_radius,
    final_radius,
    fastener_diameter,
    stencil_thickness,
    stencil_width,
    max_segment_size,
):
    """Generate a single arc-segment stencil with 2 drill guide holes.

    The arc spans the same angle as one Spray_Rig segment. The two holes
    sit at angle/6 and 5*angle/6 within that arc, at mid_radius.

    Parameters
    ----------
    initial_radius : float
        radius_minor of the spray arrays
    final_radius : float
        radius_major of the spray arrays
    fastener_diameter : float
        diameter of the cone barb base — the hole size in the stencil
    stencil_thickness : float
        how thick the stencil plate is (mm)
    stencil_width : float
        radial width of the stencil ring (mm), centred at mid_radius
    max_segment_size : float
        arc length limit that determines segment angle (must match
        Spray_Rig_Interconnect for holes to align)
    """
    assert initial_radius < final_radius, "radius_minor must be less than radius_major"

    # --- Segment count logic (mirrors Spray_Rig_Interconnect.spray_rig) ---
    final_circumference = 2 * pi * final_radius
    divisors = []
    for i in range(1, floor(final_circumference)):
        divisors.append(final_circumference / i)
    divisors = [x for x in divisors if x < max_segment_size]
    closest_divisor = min(divisors, key=lambda x: abs(x - max_segment_size))
    num_segments = final_circumference / closest_divisor
    angle = degrees(closest_divisor / final_radius)       # segment arc in degrees

    mid_radius = (initial_radius + final_radius) / 2
    inner_r = mid_radius - stencil_width / 2
    outer_r = mid_radius + stencil_width / 2
    hole_r = fastener_diameter / 2

    print("=== Stencil Segment ===")
    print(f"  mid_radius:        {mid_radius:.2f} mm")
    print(f"  stencil_width:     {stencil_width:.1f} mm")
    print(f"  inner radius:      {inner_r:.2f} mm")
    print(f"  outer radius:      {outer_r:.2f} mm")
    print(f"  segment angle:     {angle:.3f} deg")
    print(f"  holes:             2 (at {angle/6:.1f}° and {5*angle/6:.1f}°)")
    print(f"  hole diameter:     {fastener_diameter:.1f} mm")
    print(f"  thickness:         {stencil_thickness:.1f} mm")

    # --- 2D ring sector for one segment ---
    outer = circle(r=outer_r, _fn=0)
    inner = circle(r=inner_r, _fn=0)
    ring_2d = outer - inner

    ang = radians(angle)
    size = outer_r * 2
    wedge = polygon([[0, 0], [size, 0], [size * cos(ang), size * sin(ang)]])
    sector_2d = ring_2d * wedge

    segment = linear_extrude(height=stencil_thickness, center=True)(sector_2d)

    # --- Drill guide holes (over-length to punch cleanly through) ---
    hole = cylinder(r=hole_r, h=stencil_thickness * 3, center=True, _fn=0)

    hole1 = hole.translate([mid_radius, 0, 0]).rotate([0, 0, angle / 6])
    hole2 = hole.translate([mid_radius, 0, 0]).rotate([0, 0, 5 * angle / 6])
    segment -= hole1
    segment -= hole2

    return segment


if __name__ == "__main__":
    config = toml.load("configuration.toml")
    stencil_params = {
        "initial_radius": config["initial_radius"],
        "final_radius": config["final_radius"],
        "fastener_diameter": config["fastener_diameter"],
        "stencil_thickness": config["stencil_thickness"],
        "stencil_width": config["stencil_width"],
        "max_segment_size": config["max_segment_size"],
    }
    obj = stencil(**stencil_params)

    scad_file = "Spray_Rig_Stencil.scad"
    stl_file = "Spray_Rig_Stencil.stl"

    scad_render_to_file(obj, scad_file)

    header = "$fa = 1; $fs = 0.5;\n"
    with open(scad_file, "r+") as f:
        content = f.read()
        f.seek(0)
        f.write(header + content)

    print(f"\nSCAD written to {scad_file}")

    cmd = ["openscad", "-q", "--export-format", "binstl", "-o", stl_file, scad_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR rendering STL: {result.stderr}")
    else:
        print(f"STL written to {stl_file}")
