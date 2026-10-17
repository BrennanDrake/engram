from setuptools import find_packages, setup

package_name = 'engram_tools'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', [f'resource/{package_name}']),
        (f'share/{package_name}', ['package.xml']),
    ],
    install_requires=['setuptools'],
    extras_require={'test': ['pytest']},
    zip_safe=True,
    maintainer='Brennan Drake',
    maintainer_email='brennan.drake47903@gmail.com',
    description='Operational tools for the engram robot: health checks and link diagnostics.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'health_check = engram_tools.health_check:main',
            'link_check = engram_tools.link_check:main',
        ],
    },
)
