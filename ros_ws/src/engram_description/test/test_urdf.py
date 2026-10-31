"""The xacro expands, and the arm is mounted centred on the Waffle top plate."""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

URDF = Path(__file__).resolve().parents[1] / 'urdf' / 'engram.urdf.xacro'


def expand(*args: str) -> ET.Element:
    out = subprocess.run(['xacro', str(URDF), *args], check=True, capture_output=True, text=True)
    return ET.fromstring(out.stdout)


def mount_joint(robot: ET.Element) -> ET.Element:
    return next(j for j in robot.findall('joint') if j.get('name') == 'arm_mount_joint')


def test_xacro_expands_to_base_and_arm() -> None:
    robot = expand()
    links = {link.get('name') for link in robot.findall('link')}
    assert {'base_footprint', 'base_link', 'base_scan'} <= links
    assert {'arm_base_link', 'arm_gripper_link'} <= links
    assert not any(m.get('filename').startswith('assets/') for m in robot.iter('mesh'))


def origin(joint: ET.Element) -> list[float]:
    return [float(v) for v in joint.find('origin').get('xyz').split()]


def test_arm_stands_on_deck_with_pan_axis_over_centre() -> None:
    joint = mount_joint(expand())
    assert joint.find('parent').get('link') == 'top_deck_link'
    x, y, z = origin(joint)
    assert abs(x + 0.0388) < 1e-6
    assert y == 0.0
    assert abs(z - 0.0024) < 1e-6


def test_deck_clears_lidar() -> None:
    deck = next(j for j in expand().findall('joint') if j.get('name') == 'top_deck_joint')
    lidar_top = 0.122 + 0.009  # base_scan height + top of lds.stl
    assert origin(deck)[2] - 0.009 > lidar_top  # plate underside is 9 mm down


def test_without_deck_arm_sits_on_waffle_plate() -> None:
    joint = mount_joint(expand('top_deck:=false'))
    assert joint.find('parent').get('link') == 'base_link'
    x, y, z = origin(joint)
    assert (x, y) == (0.0222, 0.0)
    assert abs(z - 0.0939) < 1e-6


def test_arm_x_overrides_default_in_base_link() -> None:
    assert origin(mount_joint(expand('top_deck:=false', 'arm_x:=0.03')))[0] == 0.03
    assert abs(origin(mount_joint(expand('arm_x:=-0.09')))[0] - (-0.09 + 0.064)) < 1e-9


def test_deck_has_ten_standoffs_reaching_the_waffle_plate() -> None:
    deck = next(link for link in expand().findall('link') if link.get('name') == 'top_deck_link')
    standoffs = deck.findall('visual/geometry/cylinder')
    assert len(standoffs) == 10
    assert all(abs(float(c.get('length')) - (0.055 - 0.009)) < 1e-9 for c in standoffs)
