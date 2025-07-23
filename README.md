# playwright cityglow test

https://playwright.dev/python/docs/library

## setup venv
1. `python3 -m venv venv`
2. `source venv/bin/activate`

## install dependencies
1. `pip install -r requirements.txt`
2. `playwright install`

## run
1. `python test.py`

in the playwright inspector, hit the green `resume (F8)` arrow at top to start

or set `PAUSE_MODE` to `False` in `test.py`

change parameters at bottom of `test.py`:

```python
if __name__ == "__main__":
    make_appointment(
        first_name="Ross",
        last_name="Massey", 
        phone="123456",
        email="ross@ross.com",
        service="Facials",
        sub_service="HydraFacial FIRST TIME SPECIAL!",
        addons=["Extractions", "Dermaplaning"],  # None for no addons
        staff="Elena",  # None for "Anyone"
        day=15,
        month=8,
        year=2025,
        time="2:00 pm"
    )
```
