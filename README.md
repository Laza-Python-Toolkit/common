# Laza Common

A set of common python utility modules.




## Installation

Install from [PyPi](https://pypi.org/project/laza-common/)

```
pip install laza-di
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



## Documentation

Coming soon.


## Production

__This package is still in active development and should not be used in production environment__

