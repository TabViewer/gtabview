gtabview
-------------------------------
a graphical tabular data viewer
===============================

Stand-alone usage
-----------------

  ./gtabview.py data.csv

Usage as the default Pandas viewer
----------------------------------

Copy ``gtabview.py`` into your ``PYTHONPATH``, then:

.. code:: python

    # setup gtabview
    import pandas as pd
    import gtabview
    pd.tools.interact.interact_list = gtabview.view
    
    # generate some data
    import pandas.io.data as web
    import datetime
    start = datetime.datetime(2010, 1, 1)
    end = datetime.datetime(2013, 1, 27)
    panel = web.DataReader(["F", "YHOO"], 'yahoo', start, end) # Panel
    df = panel.loc[:,:,"F"]

    # visualize it
    df.interact()
