import os
from integrations.whatsapp import send_message, get_media_url, download_media
from integrations.drive import upload_image
from integrations.claude_client import review_caption
from integrations.meta_ads import create_ad, set_ad_id
from utils.state import get_state, set_state, next_ad_code

DEFAULT_CAPTION = (
    "🌟 LIC Bima Sakhi Yojana — Karnal ki Mahilaon ke Liye\n\n"
    "✅ Ghar se kaam karo\n"
    "✅ Pehle saal ₹7,000/mahina stipend\n"
    "✅ Plus commission har policy par\n"
    "✅ IC-38 training free\n\n"
    "Registration fee sirf ₹860\n\n"
    "Interested hain? Abhi message karein!"
)


def handle_creative_launch(message, from_phone):
    msg_type = message.get('type')

    if msg_type == 'video':
        video = message.get('video', {})
        media_id = video.get('id')
        try:
            url = get_media_url(media_id)
            video_bytes, mime = download_media(url)
            upload_image(video_bytes, f"bima_sakhi_video_{media_id}.mp4", mime_type='video/mp4')
        except Exception as e:
            print(f"Video Drive upload error: {e}")

        send_message(
            from_phone,
            "✅ Video Drive par save ho gaya.\n\n"
            "Video ad banane ke liye *Ads Manager* use karo — "
            "Meta ki API abhi video ads directly support nahi karta.\n\n"
            "Ads Manager → Create Ad → Video upload karo → "
            f"WhatsApp link: https://wa.me/{os.getenv('WHATSAPP_DISPLAY_NUMBER', '')}?text=Hi%20V1"
        )
        return

    if msg_type not in ('image', 'document'):
        return

    if msg_type == 'document':
        doc = message.get('document', {})
        mime = doc.get('mime_type', '')
        if not mime.startswith('image/'):
            send_message(from_phone, "❌ Sirf image files accept hoti hain (JPG/PNG).")
            return
        media_obj = doc
    else:
        media_obj = message.get('image', {})

    media_id = media_obj.get('id')
    caption = media_obj.get('caption', '').strip() or DEFAULT_CAPTION

    set_state('pendingCreative', {'mediaId': media_id, 'caption': caption})
    send_message(
        from_phone,
        f"📸 Image mili! Caption:\n\n_{caption}_\n\n"
        "Review ho raha hai... ek second."
    )

    review = review_caption(caption)

    if review.get('reviewFailed'):
        set_state('pendingCreative', None)
        send_message(from_phone, "❌ Caption check nahi ho paya. Baad mein try karo.")
        return

    if review.get('hasRiskyContent'):
        warning = review.get('warning', 'Content issue')
        suggestion = review.get('suggestion', '')
        set_state('pendingCreative', None)
        msg = f"⚠️ Caption mein issue mila:\n\n{warning}"
        if suggestion:
            msg += f"\n\n💡 Suggestion: {suggestion}"
        send_message(from_phone, msg)
        return

    ad_type = 'P'
    ad_code = next_ad_code(ad_type)

    set_state('pendingConfirm', {
        'action': 'launch_creative',
        'adCode': ad_code,
        'mediaId': media_id,
        'caption': caption,
    })

    send_message(
        from_phone,
        f"✅ Caption theek lag rahi hai!\n\n"
        f"Yeh ad *{ad_code}* ke naam se save hoga (PAUSED).\n\n"
        f"Aage badhein? *HAAN* / *NAHI*"
    )


def launch_pending_creative(from_phone, text):
    pending = get_state('pendingCreative')
    if not pending:
        send_message(from_phone, "Koi pending image nahi hai. Pehle poster bhejo.")
        return

    caption = pending.get('caption', DEFAULT_CAPTION)
    media_id = pending['mediaId']
    set_state('pendingCreative', None)

    ad_type = 'P'
    ad_code = next_ad_code(ad_type)

    set_state('pendingConfirm', {
        'action': 'launch_creative',
        'adCode': ad_code,
        'mediaId': media_id,
        'caption': caption,
    })
    send_message(
        from_phone,
        f"Ad *{ad_code}* ke roop mein save hoga. Confirm karein? *HAAN* / *NAHI*"
    )


def launch_creative_after_confirm(from_phone, pending):
    media_id = pending['mediaId']
    caption = pending['caption']
    ad_code = pending['adCode']

    send_message(from_phone, "⏳ Image upload ho rahi hai, ek minute...")

    try:
        url = get_media_url(media_id)
        img_bytes, mime = download_media(url)
        image_url = upload_image(img_bytes, f"bima_sakhi_{ad_code}.jpg", mime_type=mime)
    except Exception as e:
        raise Exception(f"Drive upload fail: {e}")

    ad_id = create_ad(ad_code, image_url, caption)
    set_ad_id(ad_code, ad_id)

    send_message(
        from_phone,
        f"✅ *{ad_code} taiyaar!* (PAUSED)\n\n"
        f"Ad ID: {ad_id}\n\n"
        f"Chalu karne ke liye: *{ad_code.lower()} chalu karo*"
    )
