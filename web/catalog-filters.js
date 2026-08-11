(function exposeCatalogFilters(root, factory) {
  const filters = factory();
  if (typeof module === "object" && module.exports) module.exports = filters;
  root.GLVerseCatalogFilters = filters;
}(typeof globalThis === "undefined" ? this : globalThis, () => {
  function providersForSeries(providers, series, selectedProvider = "") {
    const availableProviderIds = new Set(
      series.flatMap((item) => item.availability.map((entry) => entry.platformId)),
    );
    return providers.filter((provider) => (
      !provider.id
      || provider.id === selectedProvider
      || availableProviderIds.has(provider.id)
    ));
  }

  return { providersForSeries };
}));
