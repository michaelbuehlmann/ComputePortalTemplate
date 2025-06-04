from typing import Optional

from pydantic import BaseModel


class DataField(BaseModel):
    # if input_name is None, the field is not read from the file but inferred by the code
    input_name: Optional[str]
    output_name: str
    units: Optional[str]
    description: str


class HydroParticleField(DataField):
    applies_to: list[str]  # "agn", "star", "dm", "gas", etc


class HydroParticleSGField(BaseModel):
    input_name: str
    # different interpretation for different particle types
    output_name: dict[str, str]
    units: dict[str, str]
    description: dict[str, str]
    applies_to: list[str]


# fmt: off
halo_fields: list[DataField] = [
    DataField(input_name="fof_halo_tag", output_name="fof_halo_tag", units=None, description="FoF halo tag"),
    DataField(input_name="fof_halo_center_x", output_name="fof_halo_center_x", units="Mpc/h comoving", description="FoF halo center x"),
    DataField(input_name="fof_halo_center_y", output_name="fof_halo_center_y", units="Mpc/h comoving", description="FoF halo center y"),
    DataField(input_name="fof_halo_center_z", output_name="fof_halo_center_z", units="Mpc/h comoving", description="FoF halo center z"),
    DataField(input_name="fof_halo_mass", output_name="fof_halo_mass", units="Msun/h", description="FoF halo mass"),
    DataField(input_name="sod_halo_mass", output_name="sod_halo_M200c", units="Msun/h", description="SOD halo mass"),
    DataField(input_name="sod_halo_radius", output_name="sod_halo_R200c", units="Mpc/h comoving", description="SOD halo radius (200c)"),
    DataField(input_name="sod_halo_cdelta", output_name="sod_halo_cdelta", units="", description="SOD halo concentration (r200c/rs)"),
]

halo_lc_fields: list[DataField] = [
    DataField(input_name="fof_halo_tag", output_name="fof_halo_tag", units="", description="FoF halo tag"),
    DataField(input_name="fof_halo_center_x", output_name="fof_halo_center_x", units="Mpc/h comoving", description="FoF halo center x"),
    DataField(input_name="fof_halo_center_y", output_name="fof_halo_center_y", units="Mpc/h comoving", description="FoF halo center y"),
    DataField(input_name="fof_halo_center_z", output_name="fof_halo_center_z", units="Mpc/h comoving", description="FoF halo center z"),
    DataField(input_name="fof_halo_mass", output_name="fof_halo_mass", units="Msun/h", description="FoF halo mass"),
    DataField(input_name="sod_halo_mass", output_name="sod_halo_M200c", units="Msun/h", description="SOD halo mass"),
    DataField(input_name="sod_halo_radius", output_name="sod_halo_R200c", units="Mpc/h comoving", description="SOD halo radius (200c)"),
    DataField(input_name="sod_halo_cdelta", output_name="sod_halo_cdelta", units="", description="SOD halo concentration (r200c/rs)"),
    DataField(input_name="chi", output_name="chi", units="Mpc/h comoving", description="Comoving distance"),
    DataField(input_name="theta", output_name="theta", units="radians", description="longitude"),
    DataField(input_name="phi", output_name="phi", units="radians", description="latitude"),
]


halo_fields_hydro: list[DataField] = [
    DataField(input_name="sod_halo_mass_bar", output_name="sod_halo_Mbar200c", units="Msun/h", description="SOD halo baryonic mass (200c)"),
    DataField(input_name="sod_halo_mass_dm", output_name="sod_halo_Mdm200c", units="Msun/h", description="SOD halo dark matter mass (200c)"),
    DataField(input_name="sod_halo_mass_gas", output_name="sod_halo_MGas200c", units="Msun/h", description="SOD halo gas mass (200c)"),
    DataField(input_name="sod_halo_mass_star", output_name="sod_halo_MStar200c", units="Msun/h", description="SOD halo stellar mass (200c)"),
    DataField(input_name="sod_halo_M500c", output_name="sod_halo_M500c", units="Msun/h", description="SOD halo mass (500c)"),
    DataField(input_name="sod_halo_MGas500c", output_name="sod_halo_MGas500c", units="Msun/h", description="SOD halo gas mass (500c)"),
    DataField(input_name="sod_halo_MStar500c", output_name="sod_halo_MStar500c", units="Msun/h", description="SOD halo stellar mass (500c)"),
    DataField(input_name="sod_halo_R500c", output_name="sod_halo_R500c", units="Mpc/h comoving", description="SOD halo radius (500c)"),
    DataField(input_name="sod_halo_M2500c", output_name="sod_halo_M2500c", units="Msun/h", description="SOD halo mass (2500c)"),
    DataField(input_name="sod_halo_MGas2500c", output_name="sod_halo_MGas2500c", units="Msun/h", description="SOD halo gas mass (2500c)"),
    DataField(input_name="sod_halo_MStar2500c", output_name="sod_halo_MStar2500c", units="Msun/h", description="SOD halo stellar mass (2500c)"),
    DataField(input_name="sod_halo_R2500c", output_name="sod_halo_R2500c", units="Mpc/h comoving", description="SOD halo radius (2500c)"),
    DataField(input_name="sod_halo_MVir", output_name="sod_halo_MVir", units="Msun/h", description="SOD halo mass (virial definition)"),
    DataField(input_name="sod_halo_MGasVir", output_name="sod_halo_MGasVir", units="Msun/h", description="SOD halo gas mass (virial definition)"),
    DataField(input_name="sod_halo_MStarVir", output_name="sod_halo_MStarVir", units="Msun/h", description="SOD halo stellar mass (virial definition)"),
    DataField(input_name="sod_halo_RVir", output_name="sod_halo_RVir", units="Mpc/h comoving", description="SOD halo radius (virial definition)"),
    DataField(input_name="sod_halo_mmagn_mass", output_name="sod_halo_mmagn_mass", units="Msun/h", description="mass of the most massive AGN in the halo"),
    # Not available yet
    # DataField(input_name="sod_halo_Y500c", output_name="sod_halo_Y500c", units="(Mpc/h)^2", description="SOD halo integrated Compton Y parameter (500c)"),
]

halo_orientation_fields: list[DataField] = [
    DataField(input_name="sod_halo_eigR1X", output_name="sod_halo_eigR1X", units="", description="SOD halo reduced eigenvector 1 x component"),
    DataField(input_name="sod_halo_eigR1Y", output_name="sod_halo_eigR1Y", units="", description="SOD halo reduced eigenvector 1 y component"),
    DataField(input_name="sod_halo_eigR1Z", output_name="sod_halo_eigR1Z", units="", description="SOD halo reduced eigenvector 1 z component"),
    DataField(input_name="sod_halo_eigR2X", output_name="sod_halo_eigR2X", units="", description="SOD halo reduced eigenvector 2 x component"),
    DataField(input_name="sod_halo_eigR2Y", output_name="sod_halo_eigR2Y", units="", description="SOD halo reduced eigenvector 2 y component"),
    DataField(input_name="sod_halo_eigR2Z", output_name="sod_halo_eigR2Z", units="", description="SOD halo reduced eigenvector 2 z component"),
    DataField(input_name="sod_halo_eigR3X", output_name="sod_halo_eigR3X", units="", description="SOD halo reduced eigenvector 3 x component"),
]

# Additional fields if profiles are requested
halo_fields_profiles: list[DataField] = [
    DataField(input_name=None, output_name="profile_index", units="", description="Row index of corresponding profile in profile catalog. -1 if no profile."),
]

# Additional fields if galaxies are requested
halo_fields_galaxies: list[DataField] = [
    DataField(input_name=None, output_name="galaxy_index_start", units="", description="Start index of corresponding galaxies in galaxy catalog."),
    DataField(input_name=None, output_name="galaxy_index_end", units="", description="End index of corresponding galaxies in galaxy catalog (exclusive)."),
]

profile_fields: list[DataField] = [
    DataField(input_name="fof_halo_bin_tag", output_name="fof_halo_tag", units="", description="FoF halo tag"),
    DataField(input_name="sod_halo_bin", output_name="bin_index", units="", description="Bin index"),
    DataField(input_name="sod_halo_bin_radius", output_name="bin_radius_right", units="Mpc/h comoving", description="Bin radius (right)"),
    DataField(input_name=None, output_name="bin_radius_left", units="Mpc/h comoving", description="Bin radius (left)"),
    DataField(input_name="sod_halo_bin_mass", output_name="bin_mass", units="Msun/h", description="Total mass in bin"),
]

profile_fields_hydro: list[DataField] = [
    DataField(input_name="sod_halo_bin_cdm_fraction", output_name="bin_cdm_fraction", units="", description="Fraction of total mass that is CDM"),
    DataField(input_name="sod_halo_bin_gas_fraction", output_name="bin_gas_fraction", units="", description="Fraction of total mass that is gas"),
    DataField(input_name="sod_halo_bin_star_fraction", output_name="bin_star_fraction", units="", description="Fraction of total mass that is stars"),
    # Not available yet
    # DataField(input_name="sod_halo_bin_zmet_fraction", output_name="bin_zmet_fraction", units="", description="Fraction of gas mass that is metal"),
    DataField(input_name="sod_halo_bin_gas_temperature", output_name="bin_gas_temperature", units="K", description="Mass weighted gas temperature"),
    DataField(input_name="sod_halo_bin_gas_entropy", output_name="bin_gas_entropy", units="", description="gas entropy in bin, defined as ln( (bin_gas_temperature/[K]) / (rho_gas/[h^2 Msun/Mpc^3])^(2/3) )"),
    DataField(input_name="sod_halo_bin_gas_pthermal", output_name="bin_gas_pthermal", units="h^2 keV / (comoving cm)^3", description="Mass weighted gas thermal pressure"),
]

profile_fields_halo = [
    # link to halos
    DataField(input_name=None, output_name="halo_index", units="", description="Index of the halo in the halo catalog the profile belongs to"),
]

galaxy_fields: list[DataField] = [
    DataField(input_name="fof_halo_tag", output_name="fof_halo_tag", units="", description="FoF halo tag"),
    DataField(input_name="gal_center_x", output_name="gal_center_x", units="Mpc/h comoving", description="Galaxy center x"),
    DataField(input_name="gal_center_y", output_name="gal_center_y", units="Mpc/h comoving", description="Galaxy center y"),
    DataField(input_name="gal_center_z", output_name="gal_center_z", units="Mpc/h comoving", description="Galaxy center z"),
    DataField(input_name="gal_radius", output_name="gal_radius", units="Mpc/h comoving", description="Galaxy aperture radius"),
    DataField(input_name="gal_half_stellar_rad", output_name="gal_half_stellar_rad", units="Mpc/h comoving", description="Galaxy half stellar mass radius"),
    DataField(input_name="gal_dbscan_radius", output_name="gal_dbscan_radius", units="Mpc/h comoving", description="Galaxy DBSCAN radius (distance to furthest star particle)"),
    DataField(input_name="gal_mass", output_name="gal_mass", units="Msun/h", description="Galaxy aperture mass"),
    DataField(input_name="gal_mass_dm", output_name="gal_mass_dm", units="Msun/h", description="Galaxy aperture dark matter mass"),
    DataField(input_name="gal_mass_gas", output_name="gal_mass_gas", units="Msun/h", description="Galaxy aperture gas mass"),
    DataField(input_name="gal_mass_star", output_name="gal_mass_star", units="Msun/h", description="Galaxy aperture stellar mass"),
    DataField(input_name="gal_mass_agn", output_name="gal_mass_agn", units="Msun/h", description="Galaxy AGN mass"),
    DataField(input_name="gal_2Rhalf_stellar_mass", output_name="gal_2Rhalf_stellar_mass", units="Msun/h", description="Galaxy stellar mass within 2 half stellar mass radius"),
    DataField(input_name="gal_dbscan_mstar", output_name="gal_dbscan_mstar", units="Msun/h", description="Galaxy DBSCAN stellar mass"),
    DataField(input_name="gal_1D_stellar_vel_disp", output_name="gal_1D_stellar_vel_disp", units="km/s", description="Galaxy (average) 1D stellar velocity dispersion"),
    # Not available yet
    # DataField(input_name="gal_LOS_stellar_vel_disp", output_name="gal_LOS_stellar_vel_disp", units="km/s", description="Galaxy line of sight stellar velocity dispersion"),
]

galaxy_fields_halo = [
    # link to halos
    DataField(input_name=None, output_name="halo_index", units="", description="Index of the halo in the halo catalog the galaxy belongs to"),
]

particle_fields: list[DataField] = [
    DataField(input_name="id", output_name="id", units="", description="Particle ID"),
    DataField(input_name="x", output_name="x", units="Mpc/h comoving", description="Particle x"),
    DataField(input_name="y", output_name="y", units="Mpc/h comoving", description="Particle y"),
    DataField(input_name="z", output_name="z", units="Mpc/h comoving", description="Particle z"),
    DataField(input_name="vx", output_name="vx", units="km/s comoving", description="Particle vx"),
    DataField(input_name="vy", output_name="vy", units="km/s comoving", description="Particle vy"),
    DataField(input_name="vz", output_name="vz", units="km/s comoving", description="Particle vz"),
]

particle_fields_halo = [
    DataField(input_name="fof_halo_tag", output_name="fof_halo_tag", units="", description="FoF halo tag"),
]

particle_fields_hydro: list[DataField] = [
    DataField(input_name="phi", output_name="phi", units="(km/s)^2 comoving", description="Particle potential"),
    DataField(input_name="mass", output_name="mass", units="Msun/h", description="Particle mass"),
    HydroParticleField(input_name="uu", output_name="uu", units="km^2/s^2 comoving", description="Particle internal energy", applies_to=["gas"]),
    HydroParticleField(input_name="hh", output_name="hh", units="Mpc/h comoving", description="normalized smoothing length", applies_to=["gas"]),
    HydroParticleField(input_name="rho", output_name="rho", units="(Msun/h) / (Mpc/h)^3 comoving", description="Particle density", applies_to=["gas"]),
    HydroParticleField(input_name="mu", output_name="mu", units="m_H", description="Particle mean molecular weight", applies_to=["gas"]),
    HydroParticleField(input_name="zmet", output_name="zmet", units="", description="metallicity (mass fraction of everything except H, He)", applies_to=["gas", "star"]),
    HydroParticleField(input_name="yhe", output_name="yhe", units="", description="helium mass fraction", applies_to=["gas", "star"]),
]

particle_fields_sg: list[HydroParticleSGField] = [
    HydroParticleSGField(input_name="tage", output_name={"agn": "age", "star": "age"}, units={"agn": "hubble time", "star": "hubble time"}, description={"agn": "AGN age", "star": "stellar age"}, applies_to=["star", "agn"]),
    HydroParticleSGField(input_name="mbh/vw", output_name={"agn": "MBH"}, units={"agn": "Msun/h"}, description={"agn": "Black hole mass"}, applies_to=["agn"]),
    HydroParticleSGField(input_name="sfr/bhr", output_name={"agn": "BHR", "star": "SFR"}, units={"agn": "Msun/yr", "star": "Msun/yr"}, description={"agn": "AGN accretion rate", "star": "Star formation rate"}, applies_to=["star", "agn"]),
]
# fmt: on
