
Journals without homepages (for vicky):

    .mode csv
    .output journals_missing_homepages.all.csv
    select * from journal where any_homepage=0;

    .mode csv
    .output journals_missing_homepages.sample.csv
    select * from journal where any_homepage=0 order by random() limit 25;

    select publisher, count(*) from journal where any_homepage=0 group by publisher order by count(*) desc limit 20;

    publisher                                                     count(*)
    ------------------------------------------------------------  ----------
    ¤                                                             33033
    Peter Lang International Academic Publishers                  1316
    Elsevier                                                      1079
    Informa UK (Taylor & Francis)                                 709
    Springer-Verlag                                               481
    OMICS Publishing Group                                        417
    Georg Thieme Verlag KG                                        355
    Wiley (John Wiley & Sons)                                     344
    SAGE Publications                                             267
    Science Publishing Group                                      259
    Al Manhal FZ, LLC                                             258
    Wiley (Blackwell Publishing)                                  220
    Bentham Science                                               211
    Egypts Presidential Specialized Council for Education and Sc  201
    Medknow Publications                                          199
    Inderscience Enterprises Ltd                                  177
    African Journals Online                                       167
    Diva Enterprises Private Limited                              166
    Scientific Research Publishing, Inc                           140
    Hindawi Limited                                               135

    Of 1360 Peter Lang journals, only have homepages for 44 of them.

    Of 64373 journals without homepages:
    
    - 35% have an ISSN-print and not an ISSN-electronic
    - 12% have an ISSN-electronic and not an ISSN-print
    - 28% have no ISSN-print/electronic breakdown (and for the others may just be missing)
    - 41% have some Crossref record (eg, any DOIs registered) (!)
    - 27% already have Wikidata entities
    - 51% have any work-level metadata in fatcat, and 23% have at least one paper preserved in fatcat


    select publisher_type, count(*) from journal where any_homepage=0 group by publisher_type order by count(*) desc;

    publisher_type                                                count(*)  
    ------------------------------------------------------------  ----------
    ¤                                                             44612     
    longtail                                                      5957      
    society                                                       3855      
    big5                                                          3548      
    commercial                                                    3378      
    unipress                                                      1556      
    oa                                                            793       
    other                                                         369       
    repository                                                    232       
    archive                                                       66        
    scielo                                                        7

