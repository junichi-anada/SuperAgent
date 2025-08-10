export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const NEW_AGENT_BUTTON_TEXT = "+ 新しいエージェントを作成";
export const NEW_CHAT_TEXT = "+ 新しいチャットを開始";

export const HAIR_COLORS = [
	{ value: "black", label: "黒髪" },
	{ value: "brown", label: "茶髪" },
	{ value: "blonde", label: "金髪" },
	{ value: "white", label: "白髪" },
	{ value: "gray", label: "銀髪" },
	{ value: "red", label: "赤髪" },
	{ value: "pink", label: "ピンク" },
	{ value: "blue", label: "青髪" },
	{ value: "green", label: "緑髪" },
	{ value: "purple", label: "紫髪" },
	{ value: "orange", label: "オレンジ" },
	{ value: "other", label: "その他" },
];

const femaleHairStyles = [
	{ value: "short bob", label: "ショートボブ" },
	{ value: "bob cut", label: "ボブカット" },
	{ value: "medium bob", label: "ミディアムボブ" },
	{ value: "semi long", label: "セミロング" },
	{ value: "long hair", label: "ロングヘア" },
	{ value: "wavy hair", label: "ウェーブヘア" },
	{ value: "curly hair", label: "カールヘア" },
	{ value: "straight hair", label: "ストレートヘア" },
	{ value: "layered cut", label: "レイヤーカット" },
	{ value: "pixie cut", label: "ピクシーカット" },
	{ value: "twin tails", label: "ツインテール" },
	{ value: "ponytail", label: "ポニーテール" },
	{ value: "bun hair", label: "お団子ヘア" },
	{ value: "half up", label: "ハーフアップ" },
	{ value: "braided hair", label: "編み込み" },
	{ value: "three braids", label: "三つ編み" },
	{ value: "chignon", label: "シニヨン" },
	{ value: "asymmetrical", label: "アシンメトリー" },
	{ value: "blunt bangs", label: "前髪ぱっつん" },
	{ value: "long bangs", label: "前髪長め" },
	{ value: "side part", label: "サイドパート" },
	{ value: "center part", label: "センターパート" },
];

const maleHairStyles = [
	{ value: "short bob", label: "ショートボブ" },
	{ value: "medium bob", label: "ミディアムボブ" },
	{ value: "semi long", label: "セミロング" },
	{ value: "long hair", label: "ロングヘア" },
	{ value: "wavy hair", label: "ウェーブヘア" },
	{ value: "curly hair", label: "カールヘア" },
	{ value: "straight hair", label: "ストレートヘア" },
	{ value: "layered cut", label: "レイヤーカット" },
	{ value: "pixie cut", label: "ピクシーカット" },
	{ value: "asymmetrical", label: "アシンメトリー" },
	{ value: "side part", label: "サイドパート" },
	{ value: "center part", label: "センターパート" },
];

const femaleBodyTypes = [
	{ value: "slim", label: "スリム" },
	{ value: "petite", label: "華奢" },
	{ value: "thin", label: "細身" },
	{ value: "average", label: "標準" },
	{ value: "plump", label: "ふっくら" },
	{ value: "chubby", label: "ぽっちゃり" },
	{ value: "glamorous", label: "グラマラス" },
	{ value: "athletic", label: "アスリート体型" },
	{ value: "model figure", label: "モデル体型" },
	{ value: "small", label: "小柄" },
	{ value: "curvy", label: "丸みのある" },
	{ value: "excellent style", label: "スタイル抜群" },
];

const maleBodyTypes = [
	{ value: "slim", label: "スリム" },
	{ value: "thin", label: "細身" },
	{ value: "average", label: "標準" },
	{ value: "athletic", label: "アスリート体型" },
	{ value: "model figure", label: "モデル体型" },
	{ value: "tall", label: "背が高い" },
	{ value: "excellent style", label: "スタイル抜群" },
];

const femaleClothings = [
	{ value: "elegant", label: "エレガント" },
	{ value: "feminine", label: "フェミニン" },
	{ value: "cute", label: "キュート" },
	{ value: "cool", label: "クール" },
	{ value: "casual", label: "カジュアル" },
	{ value: "girly", label: "ガーリー" },
	{ value: "sexy", label: "セクシー" },
	{ value: "formal", label: "フォーマル" },
	{ value: "business suit", label: "ビジネススーツ" },
	{ value: "business casual", label: "オフィスカジュアル" },
	{ value: "dress", label: "ワンピース" },
	{ value: "skirt style", label: "スカートスタイル" },
	{ value: "pants style", label: "パンツスタイル" },
	{ value: "denim style", label: "デニムスタイル" },
	{ value: "natural", label: "ナチュラル" },
	{ value: "bohemian", label: "ボヘミアン" },
	{ value: "vintage", label: "ヴィンテージ" },
	{ value: "fashion", label: "モード系" },
	{ value: "street style", label: "ストリート系" },
	{ value: "sporty", label: "スポーティー" },
	{ value: "resort style", label: "リゾート風" },
	{ value: "traditional japanese", label: "和装" },
	{ value: "uniform", label: "制服" },
	{ value: "nurse uniform", label: "ナース服" },
	{ value: "teacher style", label: "教師風" },
];

const maleClothings = [
	{ value: "cool", label: "クール" },
	{ value: "casual", label: "カジュアル" },
	{ value: "formal", label: "フォーマル" },
	{ value: "business suit", label: "ビジネススーツ" },
	{ value: "business casual", label: "オフィスカジュアル" },
	{ value: "pants style", label: "パンツスタイル" },
	{ value: "denim style", label: "デニムスタイル" },
	{ value: "natural", label: "ナチュラル" },
	{ value: "vintage", label: "ヴィンテージ" },
	{ value: "fashion", label: "モード系" },
	{ value: "street style", label: "ストリート系" },
	{ value: "sporty", label: "スポーティー" },
	{ value: "resort style", label: "リゾート風" },
	{ value: "traditional japanese", label: "和装" },
	{ value: "uniform", label: "制服" },
	{ value: "teacher style", label: "教師風" },
];

const femaleRelationships = [
	{ value: "friend", label: "友人" },
	{ value: "colleague", label: "同僚" },
	{ value: "family", label: "家族" },
	{ value: "teacher", label: "先生" },
	{ value: "neighbor", label: "隣人" },
	{ value: "classmate", label: "クラスメート" },
	{ value: "boss", label: "上司" },
	{ value: "subordinate", label: "部下" },
	{ value: "lover", label: "恋人" },
	{ value: "acquaintance", label: "知人" },
	{ value: "sister", label: "姉妹" },
	{ value: "daughter", label: "娘" },
	{ value: "mother", label: "母親" },
	{ value: "grandmother", label: "祖母" },
	{ value: "senior", label: "先輩" },
	{ value: "junior", label: "後輩" },
	{ value: "mentor", label: "メンター" },
	{ value: "counselor", label: "カウンセラー" },
	{ value: "assistant", label: "アシスタント" },
];

const maleRelationships = [
	{ value: "friend", label: "友人" },
	{ value: "colleague", label: "同僚" },
	{ value: "family", label: "家族" },
	{ value: "teacher", label: "先生" },
	{ value: "neighbor", label: "隣人" },
	{ value: "classmate", label: "クラスメート" },
	{ value: "boss", label: "上司" },
	{ value: "subordinate", label: "部下" },
	{ value: "lover", label: "恋人" },
	{ value: "acquaintance", label: "知人" },
	{ value: "brother", label: "兄弟" },
	{ value: "son", label: "息子" },
	{ value: "father", label: "父親" },
	{ value: "grandfather", label: "祖父" },
	{ value: "senior", label: "先輩" },
	{ value: "junior", label: "後輩" },
	{ value: "mentor", label: "メンター" },
	{ value: "counselor", label: "カウンセラー" },
	{ value: "assistant", label: "アシスタント" },
];

const femaleFirstPersons = [
	{ value: "私", label: "私" },
	{ value: "あたし", label: "あたし" },
	{ value: "うち", label: "うち" },
];

const maleFirstPersons = [
	{ value: "僕", label: "僕" },
	{ value: "俺", label: "俺" },
	{ value: "私", label: "私" },
];

const allHairStyles = [...new Map([...femaleHairStyles, ...maleHairStyles].map((item) => [item.value, item])).values()];
const allBodyTypes = [...new Map([...femaleBodyTypes, ...maleBodyTypes].map((item) => [item.value, item])).values()];
const allClothings = [...new Map([...femaleClothings, ...maleClothings].map((item) => [item.value, item])).values()];
const allRelationships = [...new Map([...femaleRelationships, ...maleRelationships].map((item) => [item.value, item])).values()];
const allFirstPersons = [...new Map([...femaleFirstPersons, ...maleFirstPersons].map((item) => [item.value, item])).values()];

export const GENDER_SPECIFIC_OPTIONS = {
	female: {
		hairStyles: femaleHairStyles,
		bodyTypes: femaleBodyTypes,
		clothings: femaleClothings,
		relationships: femaleRelationships,
		firstPersons: femaleFirstPersons,
	},
	male: {
		hairStyles: maleHairStyles,
		bodyTypes: maleBodyTypes,
		clothings: maleClothings,
		relationships: maleRelationships,
		firstPersons: maleFirstPersons,
	},
	neutral: {
		hairStyles: allHairStyles,
		bodyTypes: allBodyTypes,
		clothings: allClothings,
		relationships: allRelationships,
		firstPersons: allFirstPersons,
	},
	other: {
		hairStyles: allHairStyles,
		bodyTypes: allBodyTypes,
		clothings: allClothings,
		relationships: allRelationships,
		firstPersons: allFirstPersons,
	},
	"": {
		hairStyles: allHairStyles,
		bodyTypes: allBodyTypes,
		clothings: allClothings,
		relationships: allRelationships,
		firstPersons: allFirstPersons,
	},
};