from flask import current_app as app
import requests

from API.location import create_table, save_to_db, get_location
from linebot.v3.messaging import LocationMessage, TextMessage

__all__ = (
    'store_note',
    'get_note',
)

def store_note(
    reply_token,
    message: str,
    *,
    keyword: str,
    **kwargs,
) -> None:
    """
    Store place information in note

    Args:
        reply_token
        message (str): place name from user input
        **kwargs,
    """
    location = message

    create_table()

    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = dict(
        q=message,
        format='json',
    )

    try:
        resp = requests.get(nominatim_url, params=params, headers={"User-Agent": "my-linebot/1.0"})
        resp.raise_for_status()
        json_data = resp.json()
    except Exception as e:
        # TODO: try-catch for unexpected result?
        print(e)
        pass

    if not json_data:
        app.linebot_reply_message(
            reply_token,
            reply_msg=f"❌ 找不到「{location}」的地點😢",
        )
        return
    
    save_to_db(
        title=location,
        latitude=(latitude := float(json_data[0]['lat'])),
        longitude=(longitude := float(json_data[0]['lon'])),
        address=(address := json_data[0].get('display_name', message)),
        keyword=keyword,
    )

    app.linebot_reply_message(
        reply_token,
        reply_msg=f"✅ 已存入「{location}」的相關資訊：{address}, {latitude}, {longitude}, {keyword}",
    )

    return


def get_note(
    reply_token,
    message: str,
    **kwargs,
):
    location = message

    if not (location_data := get_location(location)):
        app.linebot_reply_message(
            reply_token,
            reply_msg=f"❌ 找不到「{location}」的地點😢",
        )
    
    locations_data_list = [location_data] if isinstance(location_data, dict) else location_data
    location_messages = list(map(
        lambda item: LocationMessage(
            title=item['title'],
            address=item['address'],
            latitude=item['latitude'],
            longitude=item['longitude']
        ),
        locations_data_list[:5],
        # LINE only accept 5 messages at most
        # ref: linebot/v3/messaging/models/reply_message_request.py
    ))

    app.linebot_reply_message(
        reply_token,
        reply_msg=location_messages,
    )
    return


def search_location_neighborhood(
    reply_token,
    message: str,
    **kwargs,
):
    location = message

    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = dict(
        q=location,
        format='json',
    )

    try:
        resp = requests.get(nominatim_url, params=params, headers={"User-Agent": "my-linebot/1.0"})
        resp.raise_for_status()
        json_data = resp.json()
    except Exception as e:
        print(e)
        # TODO: try-catch for unexpected result?
        pass

    if not json_data:
        app.linebot_reply_message(
            reply_token,
            reply_msg=f"❌ 找不到「{location}」的地點😢",
        )
        return
    
    location_data = json_data[0]

    location_message = LocationMessage(
        title=location,
        address=location_data.get('display_name', location),
        latitude=(latitude := float(location_data['lat'])),
        longitude=(longitude := float(location_data['lon'])),
    )
    
    # Overpass API
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = (
        '[out:json];'
        '('
        'node["amenity"="restaurant"](around:300,{latitude},{longitude});'
        'way["amenity"="restaurant"](around:300,{latitude},{longitude});'
        'relation["amenity"="restaurant"](around:300,{latitude},{longitude});'
        ');'
        'out center;'
    ).format(latitude=latitude, longitude=longitude)

    try:
        overpass_resp = requests.post(overpass_url, data={'data': overpass_query})
        overpass_resp.raise_for_status()
        overpass_data = overpass_resp.json()
    except Exception as e:
        print(e)
        # TODO: try-catch for unexpected result?
        pass

    restaurant_names = map(
        lambda item: item.get('tags', dict()).get('name'),
        overpass_data.get("elements", list()),
    )
    # remove empty item
    restaurant_names = filter(
        None,
        restaurant_names,
    )
    restaurant_names = list(map(
        lambda item: f"🍽️  {item}",
        restaurant_names,
    ))

    if not restaurant_names:
        app.linebot_reply_message(
            reply_token,
            reply_msg=[
                location_message,
                TextMessage(f"「{location}」附近找不到具名餐廳😢"),
            ],
        )
        return
    
    app.linebot_reply_message(
        reply_token,
        reply_msg=[
            location_message,
            # NOTE: no need to limit restaurant_names name here
            TextMessage(f"「{location}」附近的美食推薦：\n{'\n'.join(restaurant_names)}")
        ],
    )
    return


