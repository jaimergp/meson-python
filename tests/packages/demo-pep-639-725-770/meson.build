project(
    'demo_pep_639_725_770',
    'c',
    version : '0.1.0',
    license : ['MIT', 'BSD-3-Clause'], # PEP 639: Meson also supports multiple licenses here
)

py = import('python').find_installation(pure: false)

py.install_sources(
    'src' / 'demo_pep_639_725_770' / '__init__.py',
    'src' / 'demo_pep_639_725_770' / 'six.py',
    subdir: 'demo_pep_639_725_770',
)

gmp = dependency('gmp', required: true)

array_ops_module = py.extension_module(
    '_gmp_ops',
    'src/demo_pep_639_725_770/_gmp_ops.c',
    dependencies: [gmp],
    install: true,
    subdir: 'demo_pep_639_725_770'
)

install_subdir(
    'sboms/',
    install_dir: join_paths(
        py.get_install_dir(),
        meson.project_name() + '-' + meson.project_version() + '.dist-info',
    ),
)
