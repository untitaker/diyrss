from diyrss import mk_app

app = mk_app({
    'CACHE_TYPE': 'simple',
    'ASSETS_AUTO_BUILD': True,
    'ASSETS_DEBUG': True
})

app.run(debug=True)
