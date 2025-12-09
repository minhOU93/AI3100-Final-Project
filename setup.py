from setuptools import setup

setup(
    name="NeRFViewer",
    version="1.0",
    description="First-person 3D mesh viewer",
    options={
        "build_apps": {
            # Main executable entry point
            "gui_apps": {
                "NeRFViewer": "main.py",
            },

            # Include all models, textures, materials, etc.
            "include_patterns": [
                "model/*.obj",
                "model/*.mtl",
                "model/*.png",
                "audio/*",
            ],
            
            "plugins": [
                "pandagl",
                "p3openal_audio",
                "p3tinyobj",
                "p3ptloader",
                "p3tinydisplay",
                "p3txload",
            ]
        }
    }
)
