# FoxholePythonAPI

An [updated] python wrapper for the foxhole [war api](https://github.com/clapfoot/warapi)

Forked from [JonnyPtn's](https://github.com/JonnyPtn) : [foxholewar](https://github.com/JonnyPtn/foxholewar)

## Usage

```python
from foxholewar import Client

# create the client
clients = [Client('live1'), 
           Client('live2')]

for client in clients:
    print(f'@{client.api_address}')
    # get the list of maps
    maps = client.fetch_map_list()

    for current_map in maps:
        # print the map data
        print(current_map)
        # get report of the current map
        print(client.fetch_report(current_map))

    # print the current war number
    war = client.fetch_current_war()
    print(war)
    print()

```

Contributions welcome, and feel free to request any additions or changes.
