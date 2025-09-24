import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import json
from datetime import datetime, timedelta
import re


# self-declare def
def to_pascal_case(text):
    def pascal_word(match):
        word = match.group(0)
        return word.capitalize()

    # This regex matches words (including accented letters) and leaves punctuation/spaces untouched
    return re.sub(r"\w+", pascal_word, text)


def replace_exact_words(text, replacements):
    # Sort keys by length (desc) to handle multi-word phrases first
    sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
    # Build regex pattern for word boundaries, handling Unicode
    pattern = r"\b(" + "|".join(re.escape(k) for k in sorted_keys) + r")\b"
    # Replace using a function to look up the replacement
    return re.sub(pattern, lambda m: replacements[m.group(0)], text)


replacements = {
    "Tháng Một": "Tháng 1",
    "Tháng Hai": "Tháng 2",
    "Tháng Ba": "Tháng 3",
    "Tháng Bốn": "Tháng 4",
    "Tháng Năm": "Tháng 5",
    "Tháng Sáu": "Tháng 6",
    "Tháng Bảy": "Tháng 7",
    "Tháng Tám": "Tháng 8",
    "Tháng Chín": "Tháng 9",
    "Tháng Mười": "Tháng 10",
    "Tháng Mười Một": "Tháng 11",
    "Tháng Mười Hai": "Tháng 12",
    "Tí": "Tí (0:00 - 1:00 & 23:00 - 0:00)",
    "Sửu": "Sửu (1:00 - 3:00)",
    "Dần": "Dần (3:00 - 5:00)",
    "Mão": "Mão (5:00 - 7:00)",
    "Thìn": "Thìn (7:00 - 9:00)",
    "Tỵ": "Tỵ (9:00 - 11:00)",
    "Ngọ": "Ngọ (11:00 - 13:00)",
    "Mùi": "Mùi (13:00 - 15:00)",
    "Thân": "Thân (15:00 - 17:00)",
    "Dậu": "Dậu (17:00 - 19:00)",
    "Tuất": "Tuất (19:00 - 21:00)",
    "Hợi": "Hợi (21:00 - 23:00)",
    "Kim quỹ": "Kim quỹ - 🔴",
    "Kim đường (Bảo quang)": "Kim đường (Bảo quang) - 🔴",
    "Ngọc đường": "Ngọc đường - 🔴",
    "Tư mệnh": "Tư mệnh - 🔴",
    "Thanh long": "Thanh long - 🔴",
    "Minh đường": "Minh đường - 🔴",
    "Kim quỹ": "Kim quỹ - 🔴",
    "Bạch hổ": "Bạch hổ - ⚫️",
    "Thiên lao": "Thiên lao - ⚫️",
    "Nguyên vũ": "Nguyên vũ - ⚫️",
    "Câu trận": "Câu trận - ⚫️",
    "Thiên hình": "Thiên hình - ⚫️",
    "Chu tước": "Chu tước - ⚫️",
    "Kim - ": "Kim 🟡 - ",
    "Mộc - ": "Mộc 🟢 - ",
    "Thủy - ": "Thủy 🔵 - ",
    "Hoả - ": "Hoả 🔴 - ",
    "Thổ - ": "Thổ 🟤 - ",
}

star_replacements = {
    "Thiên phúc": "Thiên phúc 🔴",
    "Thiên tài": "Thiên tài 🔴",
    "Nguyệt không": "Nguyệt không 🔴",
    "Hoàng ân": "Hoàng ân 🔴",
    "Phúc sinh": "Phúc sinh 🔴",
    "Tuế hợp": "Tuế hợp 🔴",
    "Đại hồng sa": "Đại hồng sa 🔴",
    "Trực tinh": "Trực tinh 🔴",
    "Âm đức": "Âm đức 🔴",
    "Sinh khí": "Sinh khí 🔴",
    "Nguyệt đức hợp": "Nguyệt đức hợp 🔴",
    "U vi tinh": "U vi tinh 🔴",
    "Lục hợp": "Lục hợp 🔴",
    "Yếu yên": "Yếu yên 🔴",
    "Ngũ phú": "Ngũ phú 🔴",
    "Địa tài": "Địa tài 🔴",
    "Thiên đức": "Thiên đức 🔴",
    "Thiên hỷ": "Thiên hỷ 🔴",
    "Mẫu thương": "Mẫu thương 🔴",
    "Tục thế": "Tục thế 🔴",
    "Tam hợp": "Tam hợp 🔴",
    "Nguyệt ân": "Nguyệt ân 🔴",
    "Nguyệt đức": "Nguyệt đức 🔴",
    "ích hậu": "ích hậu 🔴",
    "Cát khánh": "Cát khánh 🔴",
    "Thiên quý": "Thiên quý 🔴",
    "Thiên thuỵ": "Thiên thuỵ 🔴",
    "Tuế đức": "Tuế đức 🔴",
    "Dịch mã": "Dịch mã 🔴",
    "Giải thần": "Giải thần 🔴",
    "Thánh tâm": "Thánh tâm 🔴",
    "Nhân chuyên": "Nhân chuyên 🔴",
    "Dân nhật,thời đức": "Dân nhật,thời đức 🔴",
    "Phổ hộ (Hội hộ)": "Phổ hộ (Hội hộ) 🔴",
    "Hoạt diệu": "Hoạt diệu 🔴",
    "Nguyệt giải": "Nguyệt giải 🔴",
    "Thiên quan": "Thiên quan 🔴",
    "Lộc khố": "Lộc khố 🔴",
    "Kính tâm": "Kính tâm 🔴",
    "Sát cống": "Sát cống 🔴",
    "Mãn đức tinh": "Mãn đức tinh 🔴",
    "Phúc hậu": "Phúc hậu 🔴",
    "Minh tinh": "Minh tinh 🔴",
    "Thiên thành": "Thiên thành 🔴",
    "Thiên ân": "Thiên ân 🔴",
    "Nguyệt tài": "Nguyệt tài 🔴",
    "Quan nhật": "Quan nhật 🔴",
    "Thiên mã": "Thiên mã 🔴",
    "Phúc hậu": "Phúc hậu 🔴",
    "Thiên cương (Diệt môn)": "Thiên cương (Diệt môn) ⚫️",
    "Băng tiêu": "Băng tiêu ⚫️",
    "Địa phá": "Địa phá ⚫️",
    "Địa tặc": "Địa tặc ⚫️",
    "Cửu không": "Cửu không ⚫️",
    "Lỗ Ban sát": "Lỗ Ban sát ⚫️",
    "Không phòng": "Không phòng ⚫️",
    "Cửu Thổ Quỷ": "Cửu Thổ Quỷ ⚫️",
    "Tứ thời cô quả": "Tứ thời cô quả ⚫️",
    "Xích khẩu": "Xích khẩu ⚫️",
    "Ngũ hư": "Ngũ hư ⚫️",
    "Trùng phục": "Trùng phục ⚫️",
    "Nhân cách": "Nhân cách ⚫️",
    "Hoang vu": "Hoang vu ⚫️",
    "Kiếp sát": "Kiếp sát ⚫️",
    "Tiểu hồng sa": "Tiểu hồng sa ⚫️",
    "Hà khôi, Cẩu giảo": "Hà khôi, Cẩu giảo ⚫️",
    "Lôi công": "Lôi công ⚫️",
    "Thần cách": "Thần cách ⚫️",
    "Thổ cấm": "Thổ cấm ⚫️",
    "Cửu Thổ Quỷ": "Cửu Thổ Quỷ ⚫️",
    "Ly Sào": "Ly Sào ⚫️",
    "Dương công kỵ": "Dương công kỵ ⚫️",
    "Hoả tinh": "Hoả tinh ⚫️",
    "Cô thần": "Cô thần ⚫️",
    "Nguyệt yếm": "Nguyệt yếm ⚫️",
    "Hoả tai": "Hoả tai ⚫️",
    "Thiên lại": "Thiên lại ⚫️",
    "Chu tước hắc đạo": "Chu tước hắc đạo ⚫️",
    "Tiểu không vong": "Tiểu không vong ⚫️",
    "Trùng tang": "Trùng tang ⚫️",
    "Thụ tử": "Thụ tử ⚫️",
    "Nguyệt hình": "Nguyệt hình ⚫️",
    "Nguyệt phá": "Nguyệt phá ⚫️",
    "Sát chủ": "Sát chủ ⚫️",
    "Ngũ quỷ": "Ngũ quỷ ⚫️",
    "Đại hao (Tử khí,Quan phù)": "Đại hao (Tử khí,Quan phù) ⚫️",
    "Thiên cương (Diệt môn)": "Thiên cương (Diệt môn) ⚫️",
    "Tiểu hao": "Tiểu hao ⚫️",
    "Nguyệt hoả (Độc hoả)": "Nguyệt hoả (Độc hoả) ⚫️",
    "Câu trận": "Câu trận ⚫️",
    "Đại không vong": "Đại không vong ⚫️",
    "Thổ ôn (Thiên cẩu)": "Thổ ôn (Thiên cẩu) ⚫️",
    "Quả tú": "Quả tú ⚫️",
    "Tam tang": "Tam tang ⚫️",
    "Ly sàng": "Ly sàng ⚫️",
    "Quỷ khốc": "Quỷ khốc ⚫️",
    "Phủ đầu dát": "Phủ đầu dát ⚫️",
    "Nguyệt kiến chuyển sát": "Nguyệt kiến chuyển sát ⚫️",
    "Tội chí": "Tội chí ⚫️",
    "Huyền vũ": "Huyền vũ ⚫️",
    "Vãng vong (Thổ kỵ)": "Vãng vong (Thổ kỵ) ⚫️",
    "Thiên ôn": "Thiên ôn ⚫️",
    "Thổ phủ": "Thổ phủ ⚫️",
    "Nguyệt hư (Nguyệt sát)": "Nguyệt hư (Nguyệt sát) ⚫️",
    "Lục bất thành": "Lục bất thành ⚫️",
    "Hoàng sa": "Hoàng sa ⚫️",
    "Phi ma sát (Tai sát)": "Phi ma sát (Tai sát) ⚫️",
    "Bạch hổ": "Bạch hổ ⚫️",
    "Thiên hoả, Thiên ngục": "Thiên hoả, Thiên ngục ⚫️",
    "Tam nương": "Tam nương ⚫️",
}


def extract_text_between_b_and_a(soup, td_selector):
    td = soup.select_one(td_selector)
    if not td:
        return None

    found_b = False
    texts = []
    for child in td.children:
        if isinstance(child, Tag) and child.name == "b":
            found_b = True
            continue
        if isinstance(child, Tag) and child.name == "a":
            break
        if found_b and isinstance(child, NavigableString):
            text = child.strip()
            if text:
                texts.append(text)
    return " ".join(texts) if texts else None


# feature def


def get_text_or_empty(soup, selector):
    el = soup.select_one(selector)
    return el.text.strip() if el else ""


def get_list_or_empty(soup, selector):
    return (
        [el.text.strip() for el in soup.select(selector)]
        if soup.select(selector)
        else []
    )


def get_day_data(date_str, date_str2, date_str3):
    print(date_str, date_str2, date_str3)
    # Example: https://thoigian.com.vn/?mPage=D120250917
    url = f"https://thoigian.com.vn/?mPage=D1{date_str}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    url2 = f"https://licham.vn/lich-ngay-{date_str2}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Referer": "https://licham.vn/",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
    }
    try:
        response2 = requests.get(url2, headers=headers, timeout=15)
        response2.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url2}: {e}")
        print("Response content:", getattr(response2, "text", "No response"))
        return None

    soup2 = BeautifulSoup(response2.text, "html.parser")

    url3 = (
        f"https://baomoi.com/tien-ich-lich-van-nien.epi?activeTab=day&day={date_str3}"
    )
    response3 = requests.get(url3)
    if response3.status_code != 200:
        print(f"Failed to fetch {url3}")
        return None

    soup3 = BeautifulSoup(response3.text, "html.parser")

    # TODO: Update these selectors to match Thoigian.com.vn's HTML structure!
    solar_date = replace_exact_words(
        to_pascal_case(get_text_or_empty(soup, "#m601")), replacements
    )  # e.g. "Thứ Hai, Ngày 22 Tháng 9 Năm 2025"

    lunar_date = replace_exact_words(
        to_pascal_case(extract_text_between_b_and_a(soup, "#m603")[:-1]), replacements
    )  # e.g. "Ngày 26 Tháng 7 Năm 2025"

    detail_lunar_date = to_pascal_case(
        extract_text_between_b_and_a(soup, "#m604")
    )  # e.g. "Ngày Kỷ Sửu, tháng Giáp Thân, năm Ất Tỵ"

    all_time_detail = get_list_or_empty(soup, "#m609")
    all_time = [
        "{} {}".format(
            replace_exact_words(item.replace("Giờ: ", ""), replacements),
            (
                "- " + replace_exact_words(all_time_detail[i], replacements)
                if i < len(all_time_detail)
                else ""
            ),
        )
        for i, item in enumerate(get_list_or_empty(soup, "#m606"))
    ]
    good_time = [item for item in all_time if "🔴" in item]
    bad_time = [
        item for item in all_time if "⚫️" in item
    ]  # e.g. ["Bính Dần (3h-5h)", ...]

    tr_ye = soup3.select_one('tr.rc-table-row.rc-table-row-level-0[data-row-key="Năm"]')
    year_element_raw = to_pascal_case(
        tr_ye.find_all("td")[1].get_text(separator=" - ", strip=True)
    )
    year_element = replace_exact_words(
        year_element_raw, replacements
    )  # e.g. "Hoả - Phú Đăng Hoả"

    ss = get_list_or_empty(soup, "#m614")[7]
    tr_ss = soup3.find("tr", {"data-row-key": "Mùa: Mùa thu"})
    if tr_ss:
        # Get the text inside the second <td>
        tds = tr_ss.find_all("td")
        if len(tds) > 1:
            content = tds[1].get_text(separator="\n")
            # Extract "Kim" after "Vượng:"
            vuong_match = re.search(r"Vượng:\s*([^\n]+)", content)
            vuong = vuong_match.group(1).strip() if vuong_match else None
            # Extract "Hoả Trọng" after "Khắc:"
            khac_match = re.search(r"Khắc:\s*([^\n]+)", content)
            khac = khac_match.group(1).strip() if khac_match else None
        season_element = {
            ss: {
                "Tiết khí": get_list_or_empty(soup, "#m614")[16],
                "Vượng": vuong,
                "Khắc": khac,
            }
        }
    else:
        season_element = {ss: {"Tiết khí": "", "Vượng": "", "Khắc": ""}}

    tr_de = soup3.select_one(
        'tr.rc-table-row.rc-table-row-level-0[data-row-key="Ngày"]'
    )
    date_element_raw = re.sub(
        r",\s*",
        " (",
        to_pascal_case(tr_de.find_all("td")[1].get_text(separator=" - ", strip=True)),
        count=1,
    )
    date_element = replace_exact_words(
        date_element_raw + ")", replacements
    )  # e.g. "Hoả - Bích Lôi Hoả"

    bad_for_age_list = get_list_or_empty(soup, "#m614")
    bad_for_age = [
        item.strip() for item in re.split(r"[;,]", bad_for_age_list[14]) if item.strip()
    ]
    # e.g. ["Đinh Mùi", "Ất Mùi"]

    star = soup2.find("label", string="Tên sao").next_sibling.replace(":", "").strip()

    animal = get_list_or_empty(soup, "#m614")[22]  # e.g. "Giun"

    division = {
        get_list_or_empty(soup, "#m614")[24]: get_list_or_empty(soup, "#m614")[25]
    }  # e.g. "Định"

    all_star = get_list_or_empty(soup, "#m615>#m614")[30:-6]
    # Create all_star_filter: [{"Thiên phúc":{"✅":"Tốt"}}, {"❌":""}, ...] (1st, 4th, etc.)
    all_star_filter = []
    for i in range(0, len(all_star), 3):
        name = replace_exact_words(all_star[i], star_replacements)
        status = all_star[i + 1] if i + 1 < len(all_star) else ""
        note = all_star[i + 2] if i + 2 < len(all_star) else ""
        entry = {name: {"🍀": status, "🧿": note}}
        all_star_filter.append(entry)

    auspicious_star = [
        entry
        for entry in all_star_filter
        if any("🔴" in k or "🔴" in v for k, v in entry.items())
    ]
    inauspicious_star = [
        {
            k.replace("🍀", "⚠️").replace("🧿", "🧿"): {
                kk.replace("🍀", "⚠️")
                .replace("🧿", "🧿"): vv.replace("🍀", "⚠️")
                .replace("🧿", "🧿")
                for kk, vv in v.items()
            }
        }
        for entry in all_star_filter
        for k, v in entry.items()
        if any("⚫️" in k or "⚫️" in val for val in v.values())
    ]
    # print(get_list_or_empty(soup, '#m614'))
    depart = {
        "Hỷ thần": get_list_or_empty(soup, "#m614")[27],
        "Tài thần": get_list_or_empty(soup, "#m614")[29],
    }

    return {
        "date": solar_date,
        "lunar-date": lunar_date,
        "detail-lunar-date": detail_lunar_date,
        "all-time": all_time,
        "good-time": good_time,
        "bad-time": bad_time,
        "season-element": season_element,
        "year-element": year_element,
        "date-element": date_element,
        "bad-for-age": bad_for_age,
        "star": star,
        "animal": animal,
        "division": division,
        "auspicious-star": auspicious_star,
        "inauspicious-star": inauspicious_star,
        "depart": depart,
    }


def main():
    start_date = datetime(2025, 9, 1)
    end_date = datetime(2026, 1, 1)
    delta = timedelta(days=1)

    data = {}

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        date_str2 = current_date.strftime("%d-%m-%Y")
        date_str3 = current_date.strftime("%Y%m%d")
        key = current_date.strftime("%Y-%m-%d")
        day_data = get_day_data(date_str, date_str2, date_str3)
        if day_data:
            data[key] = day_data
        current_date += delta

    with open("lich_van_nien_thoigian_2025.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
