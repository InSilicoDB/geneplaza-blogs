module.exports = function (eleventyConfig) {
  // Static assets. Output mirrors the live URL shape: /blog/... is baked into
  // each post's `permalink`, so pathPrefix stays "/" - setting it to "/blog/"
  // as well would produce /blog/blog/...
  eleventyConfig.addPassthroughCopy({ "content/images": "blog/images" });
  eleventyConfig.addPassthroughCopy({ "content/assets": "blog/assets" });

  eleventyConfig.addFilter("date", (d) => {
    const dt = d instanceof Date ? d : new Date(d);
    return isNaN(dt) ? "" : dt.toISOString().slice(0, 10);
  });

  eleventyConfig.addFilter("isoDate", (d) => {
    const dt = d instanceof Date ? d : new Date(d);
    return isNaN(dt) ? "" : dt.toISOString();
  });

  // Posts only (excludes index, sitemap, robots)
  eleventyConfig.addCollection("posts", (api) =>
    api.getFilteredByGlob("content/*.md").sort((a, b) => b.date - a.date)
  );

  // Group by translation_key so templates can emit hreflang without re-scanning
  eleventyConfig.addFilter("translationsOf", (all, key, lang) =>
    (all || []).filter(
      (p) => key && p.data.translation_key === key && p.data.lang !== lang
    )
  );

  return {
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    dataTemplateEngine: "njk",
    dir: { input: "content", includes: "../_includes", output: "_site" },
    pathPrefix: "/",
  };
};
