from typing import TYPE_CHECKING

from lib.gpu import GPU_DEVICE_ID

if TYPE_CHECKING:
    from typing import Optional

    from numpy import ndarray
    from radis import Spectrum

import matplotlib.pyplot as plt
import numpy as np

# Spectrum simulation ##############################################################################


def transmission_spectrum(
    wl_min: float,
    wl_max: float,
    molecule: str,
    vmr: float,
    pressure: float,
    temperature: float,
    length: float,
    isotopes: str = "1",
    wavelength_step: "Optional[float]" = None,
    database: "Optional[str]" = None,
    return_spectrum: bool = False,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, "Spectrum"]:
    """
    Calculate the transmission spectrum of a molecule in air.

    Parameters
    ----------
    wl_min : float
        The minimum wavelength in nm.
    wl_max : float
        The maximum wavelength in nm.
    molecule : str
        The name of the molecule.
    vmr : float
        The volume mixing ratio of the molecule in air.
    pressure : float
        The pressure in Pa.
    temperature : float
        The temperature in K.
    length : float
        The length of the absorption path in m.
    isotopes : str, optional
        The isotopes of the molecule. Format: '1,2,3'.
    wavelength_step : float, optional
        The wavelength step in nm.
    database : str, optional
        The database to use. Either 'hitran' or 'hitemp'. Defaults to 'hitran' (defined in
        `lib.defaults`).
    return_spectrum : bool, optional
        Whether to return the spectrum object. Default is False.

    Returns
    -------
    wavelength : np.ndarray
        The wavelength array in nm.
    transmission : np.ndarray
        The transmission spectrum.
    spectrum : Spectrum, optional
        The spectrum object used for the calculation.
    """
    from radis import calc_spectrum

    from lib.conversions import (
        delta_wavelength_to_delta_wavenumber,
        pa_to_bar,
        wavelength_to_wavenumber,
        wavenumber_to_wavelength,
    )
    from lib.defaults import DATABASE, WAVELENGTH_STEP

    if database is None:
        database = DATABASE

    if wavelength_step is None:
        wavelength_step = WAVELENGTH_STEP

    pressure = pa_to_bar(pressure)
    length = length * 100
    wn_min = wavelength_to_wavenumber(wl_max)
    wn_max = wavelength_to_wavenumber(wl_min)
    central_wl = (wl_min + wl_max) / 2
    wavenumber_step = delta_wavelength_to_delta_wavenumber(wavelength_step, central_wl)

    spectrum = calc_spectrum(
        wn_min,
        wn_max,
        molecule=molecule,
        isotope=isotopes,
        pressure=pressure,
        Tgas=temperature,
        mole_fraction=vmr,
        path_length=length,
        databank=database,
        verbose=False,
        wstep=wavenumber_step,
    )

    wn, transmittance = spectrum.get("transmittance_noslit")

    if return_spectrum:
        return wavenumber_to_wavelength(wn)[::-1], transmittance[::-1], spectrum

    return wavenumber_to_wavelength(wn)[::-1], transmittance[::-1]


def transmission_spectrum_gpu(
    wl_min: float,
    wl_max: float,
    molecule: str,
    vmr: float,
    pressure: float,
    temperature: float,
    length: float,
    isotopes: str = "1",
    wavelength_step: "Optional[float]" = None,
    database: "Optional[str]" = None,
    spectrum: "Optional[Spectrum]" = None,
    exit_gpu: bool = True,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, "Optional[Spectrum]"]:
    """
    Calculate the transmission spectrum of a molecule in air using GPU.

    Parameters
    ----------
    wl_min : float
        The minimum wavelength in nm.
    wl_max : float
        The maximum wavelength in nm.
    molecule : str
        The name of the molecule.
    vmr : float
        The volume mixing ratio of the molecule in air.
    pressure : float
        The pressure in Pa.
    temperature : float
        The temperature in K.
    length : float
        The length of the absorption path in m.
    isotopes : str, optional
        The isotopes of the molecule. Format: '1,2,3'.
    wavelength_step : float, optional
        The wavelength step in nm.
    database : str, optional
        The database to use. Either 'hitran' or 'hitemp'. Defaults to 'hitran' (defined in
        `lib.defaults`).
    spectrum : Spectrum, optional
        The spectrum object to use. If None, a new spectrum object will be created.
    exit_gpu : bool, optional
        Whether to exit the GPU after calculation. Default is True.

    Returns
    -------
    wavelength : np.ndarray
        The wavelength array in nm.
    transmission : np.ndarray
        The transmission spectrum.
    spectrum : Spectrum
        The spectrum object used for the calculation.
    """

    from lib.conversions import (
        delta_wavelength_to_delta_wavenumber,
        pa_to_bar,
        wavelength_to_wavenumber,
        wavenumber_to_wavelength,
    )
    from lib.defaults import DATABASE, WAVELENGTH_STEP

    if database is None:
        database = DATABASE

    if wavelength_step is None:
        wavelength_step = WAVELENGTH_STEP

    pressure = pa_to_bar(pressure)
    length = length * 100
    wn_min = wavelength_to_wavenumber(wl_max)
    wn_max = wavelength_to_wavenumber(wl_min)
    central_wl = (wl_min + wl_max) / 2
    wavenumber_step = delta_wavelength_to_delta_wavenumber(wavelength_step, central_wl)

    if spectrum is None:
        import contextlib

        from radis import SpectrumFactory

        sf = SpectrumFactory(
            wn_min,
            wn_max,
            molecule=molecule,
            isotope=isotopes,
            wstep=wavenumber_step,
        )

        with contextlib.redirect_stdout(None):  # Remove to see what GPU is being used
            sf.fetch_databank(database)

            spectrum = sf.eq_spectrum_gpu(
                Tgas=temperature,
                pressure=pressure,
                mole_fraction=vmr,
                path_length=length,
                exit_gpu=False,
                device_id=GPU_DEVICE_ID,
            )
    else:
        spectrum.recalc_gpu(
            Tgas=temperature,
            pressure=pressure,
            mole_fraction=vmr,
            path_length=length,
        )

    wn, transmittance = spectrum.get("transmittance_noslit")

    if exit_gpu:
        spectrum.exit_gpu()

    return wavenumber_to_wavelength(wn)[::-1], transmittance[::-1], spectrum


def wavelength_range(
    wl_min: float, wl_max: float, wavelength: np.ndarray, spectrum: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Filter a spectrum to a wavelength range.

    Parameters
    ----------
    wl_min : float
        The minimum wavelength in nm.
    wl_max : float
        The maximum wavelength in nm.
    wl : np.ndarray
        The wavelength array in nm.
    spectrum : np.ndarray
        The spectrum array.

    Returns
    -------
    wavelength : np.ndarray
        The filtered wavelength array in nm.
    spectrum : np.ndarray
        The filtered spectrum array.
    """
    if wl_min > wl_max:
        raise ValueError("`wl_min` must be less than `wl_max`.")
    mask = (wavelength >= wl_min) & (wavelength <= wl_max)
    return wavelength[mask], spectrum[mask]


class Simulator:
    def __init__(self, **kwargs: "dict[str, str | float]") -> None:
        """Simulator for computing the transmission spectrum of a molecule.

        Parameters
        ----------
        molecule : str
            The name of the molecule.
        vmr : float
            The volume mixing ratio of the molecule in air.
        pressure : float
            The pressure in Pa.
        temperature : float
            The temperature in K.
        length : float
            The length of the absorption path in m.

        Other Parameters
        ----------------
        isotopes : str, optional
            The isotopes of the molecule. Format: '1,2,3'.
        database : str, optional
            The database to use. Either 'hitran' or 'hitemp'. Defaults to 'hitran' (defined in
            `lib.defaults`).
        wavelength_step : float, optional
            The wavelength step in nm.
        use_gpu : bool, optional
            Whether to use GPU for the calculation. Default is False.
        spectrum: Spectrum, optional
            The spectrum object to use when `use_gpu` is True. If None given and `use_gpu` is True,
            a new spectrum object will be created.
        """
        from lib.defaults import DATABASE, WAVELENGTH_STEP

        required_kwargs = ["molecule", "vmr", "pressure", "temperature", "length"]
        for key in required_kwargs:
            if key not in kwargs:
                raise ValueError(f"Missing specification for: {key}.")

        self._molecule: str = kwargs.get("molecule")
        self.vmr: float = kwargs.get("vmr")
        self.pressure: float = kwargs.get("pressure")
        self.temperature: float = kwargs.get("temperature")
        self.length: float = kwargs.get("length")
        self._wl_min: "Optional[float]" = None
        self._wl_max: "Optional[float]" = None
        self._wavelength: "Optional[ndarray]" = None
        self._transmission: "Optional[ndarray]" = None
        self._computed_vmr = None
        self._computed_pressure = None
        self._computed_temperature = None
        self._computed_length = None
        self._isotopes: str = kwargs.get("isotopes", "1")
        self._database: str = kwargs.get("database", DATABASE)
        self._wavelength_step: float = kwargs.get("wavelength_step", WAVELENGTH_STEP)
        self._use_gpu: bool = kwargs.get("use_gpu", False)
        self._spectrum: "Optional[Spectrum]" = None

    @property
    def spectrum(self) -> "Optional[Spectrum]":
        """The spectrum object used for the calculation."""
        return self._spectrum

    @property
    def molecule(self) -> str:
        """The name of the molecule."""
        return self._molecule

    @property
    def wavelength(self) -> "Optional[list]":
        """The wavelength array in nm."""
        return self._wavelength

    @property
    def transmission(self) -> "Optional[list]":
        """The transmission spectrum."""
        return self._transmission

    @property
    def use_gpu(self) -> bool:
        """Whether to use GPU for the calculation."""
        return self._use_gpu

    def compute_transmission_spectrum(
        self, wl_min: float, wl_max: float, exit_gpu: bool = True
    ) -> None:
        """
        Calculate the transmission spectrum of the molecule in air.

        Parameters
        ----------
        wl_min : float
            The minimum wavelength in nm.
        wl_max : float
            The maximum wavelength in nm.
        exit_gpu : bool, optional
            Whether to exit the GPU after calculation. Only applies if using GPU. Default is True.
        """
        sim_params = [
            self.vmr,
            self.pressure,
            self.temperature,
            self.length,
            wl_min,
            wl_max,
        ]
        sim_params_computed = [
            self._computed_vmr,
            self._computed_pressure,
            self._computed_temperature,
            self._computed_length,
            self._wl_min,
            self._wl_max,
        ]

        # If paraemters have not changed since the last calculation, return the current results.

        if all(
            param == computed_param
            for param, computed_param in zip(sim_params, sim_params_computed)
        ):
            if self._wavelength is not None and self._transmission is not None:
                return self._wavelength, self._transmission

        # Compute the transmission spectrum.

        spectrum = (
            self._spectrum
            if self._wl_min == wl_min and self._wl_max == wl_max
            else None
        )

        kwargs = dict(
            wl_min=wl_min,
            wl_max=wl_max,
            molecule=self._molecule,
            vmr=self.vmr,
            pressure=self.pressure,
            temperature=self.temperature,
            length=self.length,
            isotopes=self._isotopes,
            wavelength_step=self._wavelength_step,
            database=self._database,
            spectrum=spectrum,
            exit_gpu=exit_gpu,
            return_spectrum=True,
        )

        if self._use_gpu:
            tr_spectrum = transmission_spectrum_gpu
        else:
            tr_spectrum = transmission_spectrum

        self._wavelength, self._transmission, self._spectrum = tr_spectrum(**kwargs)

        self._wl_min = wl_min
        self._wl_max = wl_max
        self._computed_vmr = self.vmr
        self._computed_pressure = self.pressure
        self._computed_temperature = self.temperature
        self._computed_length = self.length

    def exit_gpu(self) -> None:
        """
        Exit the GPU if it was used for the calculation.
        """
        if self._use_gpu and self._spectrum is not None:
            self._spectrum.exit_gpu()

    def get_transmission_spectrum(
        self, wl_min: "Optional[float]" = None, wl_max: "Optional[float]" = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Get the transmission spectrum of the molecule in air.

        Parameters
        ----------
        wl_min : float, optional
            The minimum wavelength in nm.
        wl_max : float, optional
            The maximum wavelength in nm.

        Returns
        -------
        wavelength : np.ndarray
            The wavelength array in nm.
        transmission : np.ndarray
            The transmission spectrum.
        """
        if self._wavelength is None or self._transmission is None:
            raise ValueError("Transmission spectrum not calculated.")

        wl_min = wl_min if wl_min is not None else self._wl_min
        wl_max = wl_max if wl_max is not None else self._wl_max

        if self._wl_min > wl_min or self._wl_max < wl_max:
            raise ValueError(
                "Transmission spectrum not calculated for the specified wavelength range."
            )

        return wavelength_range(wl_min, wl_max, self._wavelength, self._transmission)

    def plot_transmission_spectrum(
        self, wl_min: "Optional[float]" = None, wl_max: "Optional[float]" = None
    ) -> plt:
        """
        Plot the transmission spectrum of the molecule in air.

        Parameters
        ----------
        wl_min : float, optional
            The minimum wavelength in nm.
        wl_max : float, optional
            The maximum wavelength in nm.

        Returns
        -------
        plt
            The matplotlib plot of the transmission spectrum.
        """
        from lib.plots import spectrum_plot

        wl, transmission = self.get_transmission_spectrum(wl_min, wl_max)

        return spectrum_plot(
            wl,
            transmission,
            f"Transmittance spectrum for {self._molecule} at {self.temperature} K, "
            + f"{self.pressure} Pa, {self.length} cm and {self.vmr} VMR",
            "Wavelength [nm]",
            "Transmittance [-]",
        )

    def show_transmission_spectrum(
        self, wl_min: "Optional[float]" = None, wl_max: "Optional[float]" = None
    ) -> None:
        """
        Show the transmission spectrum of the molecule in air.

        Parameters
        ----------
        wl_min : float, optional
            The minimum wavelength in nm.
        wl_max : float, optional
            The maximum wavelength in nm.
        """
        return self.plot_transmission_spectrum(wl_min, wl_max).show()
