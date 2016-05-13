# Mission

Provide an auto-discovery process of configurations for simple code use

# Predicted usage

- Given a directory like

        resources
        +- config
           +- management
              +- billing.yaml

- And a **billing.yaml** :

        database:
            user: "Johnny"

- When you setup your: **\_\_init__.py** to setup the quick-link

        config = ConfigProbe(
            root_path="resources/",
            patterns=["config/*/*.yaml]
        )

- anywhere else:

        import config

        print config.management.billing.database.user

        # should print "Johnny"


The patterns include * that will be used as a "namespace" and be part
of the resulting object.  The remainder is the file loaded as a dict/object,
structures like lists and dict will be available as dict/object or simple list.
