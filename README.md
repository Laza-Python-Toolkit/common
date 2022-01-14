# Laza Common

A set of common python utility modules.




## Install

Basic install
```
    pip install laza-common
```

Full install. Installs all optional dependencies.
```
    pip install laza-common[all]
```


#### Optional Dependencies

The following features/modules have additional dependecies that you might need to install:-

- `json` which requires `orjson`
    ```
    pip install laza-common[json]
    ```
- `locale` which requires `babel`
    ```
    pip install laza-common[locale]
    ```
- `moment` which requires `arrow`
    ```
    pip install laza-common[moment]
    ```
- `money` which requires `py-moneyed`
    ```
    pip install laza-common[money]
    ```
- `networks` which requires `pydantic[email]`
    ```
    pip install laza-common[networks]
    ```
- `phone` which requires `phonenumbers`
    ```
    pip install laza-common[phone]
    ```

or you can pick a set
```
pip install laza-common[phone,json,money]
```


- `money` : install `pip install laza-common[money]`
- `networks` : install `pip install laza-common[networks]`
- `phone` : install `pip install laza-common[phone]`
- or install all: `pip install laza-common[all]`

