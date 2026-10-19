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


def test_arm_mount_is_centred_on_top_plate() -> None:
    joint = mount_joint(expand())
    assert joint.find('parent').get('link') == 'base_link'
    _, y, z = (float(v) for v in joint.find('origin').get('xyz').split())
    assert y == 0.0
    assert abs(z - 0.0939) < 1e-6


def test_arm_x_is_a_launch_argument() -> None:
    joint = mount_joint(expand('arm_x:=0.03'))
    assert joint.find('origin').get('xyz').split()[0] == '0.03'
