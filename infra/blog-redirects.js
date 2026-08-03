// CloudFront Function - attach to the /blog/* cache behaviour as viewer-request.
// 1) 301s legacy WordPress URLs consolidated during the 2024 migration
// 2) rewrites directory URIs to /index.html so S3 serves the 11ty output
var REDIRECTS = {
    "/blog/en/dna-test-review-geneplaza/": "/blog/en/press/",
    "/blog/en/geneplaza-join-startit-community/": "/blog/en/press/",
    "/blog/fr/adn/": "/blog/fr/press/",
    "/blog/fr/adn-geneplaza/": "/blog/fr/press/",
    "/blog/fr/test-adn/": "/blog/fr/press/",
    "/blog/fr/geneplaza-gene-apps-store/": "/blog/fr/press/",
    "/blog/fr/geneplaza-rating-dnatestingchoice/": "/blog/fr/press/",
    "/blog/fr/adn-geneplaza-premiere-plateforme-genetique-europeenne-en-ligne/": "/blog/fr/press/",
    "/blog/fr/geneplaza-kbc-startit/": "/blog/fr/press/",
    "/blog/fr/geneplaza-start-it-community/": "/blog/fr/press/",
    "/blog/nl/genetische-aanleg/": "/blog/nl/press/",
    "/blog/nl/dna-hebbedingen/": "/blog/nl/press/",
    "/blog/nl/geneplaza-krijgt-4-5-sterren-op-5-bij-dnatestingchoice/": "/blog/nl/press/",
    "/blog/nl/geneplaza-startit-kbc/": "/blog/nl/press/",
    "/blog/nl/geneplaza-dutch-trainee-social-media/": "/blog/nl/press/",
    "/blog/en/dna-depression-risk/": "/blog/en/childhood-inflammation-depression-risk/",
    "/blog/en/k14-ancient-cultures-admixture/": "/blog/en/bell-beaker-britain-gene-pool-replacement/",
    "/blog/fr/origines-cultures-anciennes/": "/blog/fr/qui-sommes-nous-et-comment-sommes-nous-arrives-ici-david-reich-de-nouvelles-decouvertes-grace-a-ladn-ancien/"
};

function handler(event) {
    var req = event.request;
    var uri = req.uri;

    // normalise: ensure trailing slash comparison works both ways
    var lookup = uri.endsWith('/') ? uri : uri + '/';

    if (REDIRECTS[lookup]) {
        return {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers: { 'location': { value: REDIRECTS[lookup] } }
        };
    }

    // directory -> index.html (S3 origins do not do this for sub-paths)
    if (uri.endsWith('/')) {
        req.uri = uri + 'index.html';
    } else if (!uri.split('/').pop().includes('.')) {
        req.uri = uri + '/index.html';
    }
    return req;
}
