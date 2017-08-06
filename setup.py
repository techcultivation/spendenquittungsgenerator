from setuptools import setup

setup(
    name="donatr",
    py_modules=['receipt', 'zahlwort'],
    install_requires=[
        'Click',
        'uno'
    ],
    entry_points={
        "console_scripts":
        ["zahlwort=zahlwort:cli",
         "receiptgen=receipt:cli"]
    }
)
