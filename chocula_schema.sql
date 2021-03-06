
CREATE TABLE IF NOT EXISTS journal
    (issnl TEXT NOT NULL PRIMARY KEY,
     issne TEXT,
     issnp TEXT,
     fatcat_ident TEXT,
     wikidata_qid TEXT,
     name TEXT,
     publisher TEXT,
     country TEXT,
     lang TEXT,

     release_count INTEGER,
     ia_count INTEGER,
     ia_frac FLOAT,
     kbart_count INTEGER,
     kbart_frac FLOAT,
     preserved_count INTEGER,
     preserved_frac FLOAT,

     publisher_type TEXT,
     is_active BOOLEAN,
     is_oa BOOLEAN default false,
     is_longtail BOOLEAN default false,
     sherpa_color TEXT,
     has_dois BOOLEAN,
     any_homepage BOOLEAN,
     any_live_homepage BOOLEAN,
     any_gwb_homepage BOOLEAN,
     known_issnl BOOLEAN,
     valid_issnl BOOLEAN
    );

CREATE TABLE IF NOT EXISTS directory
    (issnl TEXT NOT NULL,
     slug TEXT NOT NULL,
     identifier TEXT,
     name TEXT,
     extra TEXT,
     PRIMARY KEY(issnl, slug)
    );

CREATE TABLE IF NOT EXISTS fatcat_container
    (ident TEXT NOT NULL PRIMARY KEY,
     revision TEXT NOT NULL,
     issnl TEXT,
     issne TEXT,
     issnp TEXT,
     wikidata_qid TEXT,
     name TEXT,
     container_type TEXT,
     publisher TEXT,
     country TEXT,
     lang TEXT,
     release_count INTEGER,
     ia_count INTEGER,
     ia_frac FLOAT,
     kbart_count INTEGER,
     kbart_frac FLOAT,
     preserved_count INTEGER,
     preserved_frac FLOAT
    );
CREATE INDEX IF NOT EXISTS fatcat_container_issnl_idx ON fatcat_container(issnl);

CREATE TABLE IF NOT EXISTS homepage
    (id INTEGER PRIMARY KEY,
     issnl TEXT NOT NULL,
     surt TEXT NOT NULL,
     url TEXT NOT NULL,
     host TEXT,
     domain TEXT,
     suffix TEXT,
     status_code INTEGER,
     crawl_error TEXT,
     terminal_url TEXT,
     terminal_status_code INTEGER,
     platform_software TEXT,
     issnl_in_body BOOLEAN,
     blocked BOOLEAN,
     gwb_url_success_dt TEXT,
     gwb_terminal_url_success_dt TEXT,
     UNIQUE(issnl, surt)
    );
CREATE INDEX IF NOT EXISTS homepage_url_idx ON homepage(url);
