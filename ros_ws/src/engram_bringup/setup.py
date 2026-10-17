from glob import glob

from setuptools import find_packages, setup

package_name = 'engram_bringup'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', [f'resource/{package_name}']),
        (f'share/{package_name}', ['package.xml']),
        (f'share/{package_name}/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    extras_require={'test': ['pytest']},
    zip_safe=True,
    maintainer='Brennan Drake',
    maintainer_email='brennan.drake47903@gmail.com',
    description='Launch files and the heartbeat node that start the engram robot.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'heartbeat = engram_bringup.heartbeat:main',
        ],
    },
)
