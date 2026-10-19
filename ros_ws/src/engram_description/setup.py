from glob import glob

from setuptools import setup

package_name = 'engram_description'

setup(
    name=package_name,
    version='0.1.0',
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages', [f'resource/{package_name}']),
        (f'share/{package_name}', ['package.xml']),
        (f'share/{package_name}/launch', glob('launch/*.launch.py')),
        (f'share/{package_name}/urdf', glob('urdf/*.xacro')),
        (f'share/{package_name}/meshes/so101', glob('meshes/so101/*.stl')),
        (f'share/{package_name}/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    extras_require={'test': ['pytest']},
    zip_safe=True,
    maintainer='Brennan Drake',
    maintainer_email='brennan.drake47903@gmail.com',
    description='URDF for the engram robot and an RViz viewer.',
    license='Apache-2.0',
)
