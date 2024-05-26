from loguru import logger

try:
    import skia
except ImportError as e:
    logger.error(e)
    logger.warning(
        "Missing dependent files \n\n please install dependence: \n\n ---------------------------------------\n\n "
        "Ubuntu: apt install libgl1-mesa-glx \n\n ArchLinux: pacman -S libgl \n\n Centos: yum install mesa-libGL -y "
        "\n\n---------------------------------------"
    )
    raise RuntimeError
