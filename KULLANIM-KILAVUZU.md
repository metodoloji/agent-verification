# Agent Verification: Kapsamlı Kullanıcı Kılavuzu
### (Gündelik Kullanıcılar, ChatGPT/Claude/Gemini Meraklıları ve Yazılım Geliştiriciler İçin)

[![Organization](https://img.shields.io/badge/org-metodoloji-0b7285?style=flat-square)](https://github.com/metodoloji)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE)
[![English Guide](https://img.shields.io/badge/guide-English-blue?style=flat-square)](USER-GUIDE.md)

> **"Bu proje sadece yazılımcılar için mi?"**  
> **Kesinlikle HAYIR!** Doğruluk, güvenilirlik ve halüsinasyonsuz bilgi ihtiyacı; bir evin kira sözleşmesini imzalayan kiracıdan, çocuğuna sağlık tavsiyesi arayan ebeveyne, tez yazan üniversite öğrencisinden milyon liralık alışveriş kararı veren tüketiciye kadar **herkesin** en temel ihtiyacıdır.

---

## 📑 İçindekiler

1. [Bu Kılavuz Kimler İçindir?](#1-bu-kılavuz-kimler-içindir)
2. [Geleneksel Yapay Zeka Neden Hata Yapar?](#2-geleneksel-yapay-zeka-neden-hata-yapar)
3. [ChatGPT, Claude ve Gemini'de Kod Yazmadan Nasıl Kullanılır?](#3-chatgpt-claude-ve-gemini-web-arayüzünde-nasıl-kullanılır)
   - [Yöntem A: Sihirli Tek Satırlık Prompt Eki](#yöntem-a-sihirli-tek-satırlık-prompt-eki)
   - [Yöntem B: ChatGPT "Özel Talimatlar (Custom Instructions)" Şablonu](#yöntem-b-chatgpt-özel-talimatlar-custom-instructions-şablonu)
   - [Yöntem C: Kopyala-Yapıştır Doğrulama Çerçevesi](#yöntem-c-kopyala-yapıştır-doğrulama-çerçevesi)
4. [Gündelik Yaşamdan 7 Kapsamlı Senaryo (Adım Adım & Karşılaştırmalı)](#4-gündelik-yaşamdan-7-kapsamlı-senaryo)
   - [Senaryo 1: Tüketici & Alışveriş Kararları (Teknoloji/Beyaz Eşya)](#senaryo-1-tüketici--alışveriş-kararları-laptop-robot-süpürge-araba)
   - [Senaryo 2: Hukuk & Sözleşme Denetimi (Kira ve Tahliye Taahhütnamesi)](#senaryo-2-hukuk--sözleşme-denetimi-kira-sözleşmesi-ve-tahliye)
   - [Senaryo 3: Kişisel Finans & Kredi/Yatırım Kararları](#senaryo-3-kişisel-finans--kredi-mevduat-ve-yatırım-hesabı)
   - [Senaryo 4: Sağlık, Tıp & Beslenme Teyidi (Mit Çürütme)](#senaryo-4-sağlık-tıp--beslenme-iddiaları-ve-mit-çürütme)
   - [Senaryo 5: Vize, Seyahat & Bürokrasi (90/180 Gün Kuralı)](#senaryo-5-vize-seyahat--bürokrasi-schengen-hesaplaması)
   - [Senaryo 6: Öğrenci & Akademik Araştırma (Sahte Kaynak Engeli)](#senaryo-6-öğrenci--akademik-araştırma-ve-tez-kaynakçası)
   - [Senaryo 7: Haber Doğrulama & Sosyal Medya İddiaları (Fact-Checking)](#senaryo-7-haber-doğrulama--sosyal-medya-iddiaları)
5. [Yazılım Geliştiriciler & Teknik Ekipler İçin Senaryolar](#5-yazılım-geliştiriciler--teknik-ekipler-için-senaryolar)
6. [18 Doğrulama Deseni: Hem Günlük Hayat Hem Kod Örnekleri](#6-18-doğrulama-deseni-hem-günlük-hayat-hem-kod-örnekleri)
7. [4 Doğrulama Derinliği (MINIMAL, STANDARD, ADVERSARIAL, CRITICAL)](#7-4-doğrulama-derinliği)
8. [4 Karar Durumu ve Anlamları (PASS, PWL, BLOCKED, FAIL)](#8-4-karar-durumu-ve-anlamları)
9. [2-Adımlı Revizyon Kuralı (Sonsuz Döngü Engeli)](#9-2-adımlı-revizyon-kuralı)

---

## 1. Bu Kılavuz Kimler İçindir?

* 🏠 **Günlük Kullanıcılar:** Alışveriş yapan, ev kiralayan, tatil planlayan veya ChatGPT'ye günlük sorular soran herkes.
* 🩺 **Sağlık & Yaşam Meraklıları:** Diyet, vitamin ve sağlık tavsiyelerinin bilimsel gerçekliğini sorgulayanlar.
* ⚖️ **Vatandaşlar & Hukuk Takipçileri:** Sözleşmelerindeki tuzak maddeleri ve haklarını netleştirmek isteyenler.
* 🎓 **Öğrenciler & Akademisyenler:** Uydurma referans ve sahte alıntılardan arınmış tez ve ödev hazırlayanlar.
* 💼 **İş İnsanları & Yatırımcılar:** Finansal simülasyonlarındaki gizli varsayımları görmek isteyenler.
* 💻 **Yazılımcılar & Mühendisler:** Kritik kod, veritabanı migration ve mimari kararlarını hasmane testten geçirmek isteyenler.

---

## 2. Geleneksel Yapay Zeka Neden Hata Yapar?

Standart bir yapay zekaya (ChatGPT, Gemini vb.) *"Cevabından emin misin?"* veya *"Bu doğru mu?"* diye sorduğunuzda şu 3 ölümcül sorun yaşanır:

1. **Yalancı Onaylama (Confirmation Bias):** Model az önce yazdığı cevabı tekrar okur. Tıpkı kendi yazdığı sınav kağıdını okuyan bir öğrenci gibi kendi mantık hatalarını göremez ve *"Evet, kesinlikle eminim"* der (`VF-06 / VF-07`).
2. **Pazarlama / Broşür Dili Tuzağı:** Ürün karşılaştırmalarında üreticilerin iddialı reklam metinlerini gerçek sanır; kronik arızaları veya gizli maliyetleri söylemez (`OF-03`).
3. **Halüsinasyonla Kaynak Uydurma:** Bir mahkeme kararı veya bilimsel makale sorulduğunda, kulağa çok mantıklı gelen ama gerçekte asla var olmayan sahte kaynaklar icat eder (`INV-010 / EF-01`).

**`agent-verification` Ne Yapar?**  
Modeli kendi cevabına **düşman (adversarial)** yapar. Model, yanıtı onaylamaya değil; **yanıtı çürütmeye, içindeki açıkları yakalamaya ve en zorlu köşe durumları üretmeye** zorlanır.

---

## 3. ChatGPT, Claude ve Gemini Web Arayüzünde Nasıl Kullanılır?

Herhangi bir kod yazmanıza, terminal açmanıza veya yazılımcı olmanıza gerek yoktur! Doğrudan tarayıcınızda kullanabilirsiniz.

### Yöntem A: Sihirli Tek Satırlık Prompt Eki
Sorduğunuz herhangi bir normal sorunun sonuna şu cümleyi ekleyin:

```text
[Lütfen bu çıktıyı agent-verification protokolüyle doğrula: İddiaları ayıkla, 
karşıt örnekler ve saklanan dezavantajlarla hasmane test yap, doğrulanmamış 
varsayımları açıkça listele ve nihai bir karar (PASS/PWL/BLOCKED/FAIL) bildir.]
```

---

### Yöntem B: ChatGPT "Özel Talimatlar (Custom Instructions)" Şablonu
ChatGPT'nin her zaman bu titizlikle yanıt vermesini istiyorsanız, ChatGPT Ayarlarından **"Custom Instructions (Özel Talimatlar)"** kısmındaki *"ChatGPT'nin nasıl yanıt vermesini istersiniz?"* kutusuna şunu yapıştırın:

```text
Doğruluk hassasiyeti gerektiren kararlarda, karşılaştırmalarda ve iddialarda 
'agent-verification' protokolünü uygula:
1. Kendi cevabını doğrudan onaylama; en zayıf noktasını çürütecek karşıt örnekler ara.
2. Önerdiğin şeylerin mutlaka gizli maliyetlerini, dezavantajlarını ve sınırlarını açıkla.
3. Elinde doğrulanabilir dış kanıt yoksa tahmin yürütme, BLOCKED ver ve eksik bilgiyi söyle.
4. Kıyaslamalarda her iki seçeneğe de eşit, tarafsız ve simetrik kriterler uygula.
```

---

### Yöntem C: Kopyala-Yapıştır Doğrulama Çerçevesi
Çok kritik bir karar vereceğiniz zaman şu şablonu kopyalayıp sorunuzla birlikte yapıştırın:

```text
Soru/Karar: [Buraya konunuzu yazın]

Lütfen bu görevi 'ADVERSARIAL' doğrulama derinliğinde ele al:
- Temel iddialarını listele.
- En az 2 adet çürütücü karşıt senaryo (counterexample) üret.
- Saklanan/görünmeyen varsayımları (Assumption Audit) deşifre et.
- Sonucu PASS, PASS_WITH_LIMITATIONS veya FAIL olarak bağla.
```

---

## 4. Gündelik Yaşamdan 7 Kapsamlı Senaryo

### Senaryo 1: Tüketici & Alışveriş Kararları (Laptop, Robot Süpürge, Araba)

* **Kullanıcı Sorusu:** *"50.000 TL bütçem var. Mimarlık öğrencisiyim; 3D modelleme ve render için X Marka Laptop mu yoksa Y Marka Laptop mu almalıyım?"*
* **Standart Yapay Zeka Ne Yapar?** İki bilgisayarın broşür özelliklerini alt alta yazar: *"İkisi de harika, X modelinin ekranı çok güzel, Y modelinin işlemcisi çok hızlı, bütçenize göre seçebilirsiniz."* (Kullanıcıya hiçbir fayda sağlamaz).
* **Agent-Verification ile Ne Olur?**
  * **İddia:** *"X bilgisayarı ince ve hafif kasasında render alabilir."*
  * **Hasmane Test (Saldırı):** 3D render sırasında GPU ve CPU 100W güç çeker. X modelinin soğutma bloğu tek fanlıdır. 15 dakika sonra termal darboğaz (thermal throttling) yaşanıp frekans yarıya düşer mi?
  * **Saklanan Kısıt:** X modelinde RAM anakarta lehimlidir, ileride 16 GB'tan 32 GB'a yükseltilemez (`Recommendation Verification`).
  * **Sonuç:** `PASS_WITH_LIMITATIONS`. Kullanıcıya reklam diliyle değil, gerçek kronik sorunlar ve donanım sınırlarıyla net karar verdirilir.

---

### Senaryo 2: Hukuk & Sözleşme Denetimi (Kira Sözleşmesi ve Tahliye)

* **Kullanıcı Sorusu:** *"Ev kiralayacağım. Ev sahibi kira kontratının yanına 'Tarihi boş bırakılmış tahliye taahhütnamesi' koymuş. 'Bu sadece formalite, sorun olmaz' diyor. İmzalamalı mıyım?"*
* **Standart Yapay Zeka Ne Yapar?** *"Genellikle ev sahipleri bunu talep eder, güveniyorsanız imzalayabilirsiniz ama dikkatli olun."* (Hayati bir hukuki riski hafife alır).
* **Agent-Verification ile Ne Olur?**
  * **Varsayım Denetimi (Assumption Audit):** *"Ev sahibinin taahhütnameyi kötüye kullanmayacağı"* varsayımı kanıtlanamaz bir güvendir (`UNVERIFIED`).
  * **Yargıtay İçtihadı Çapraz Sorgusu (Claim-Evidence):** Yargıtay Hukuk Genel Kurulu kararlarına göre, boş tarihe imza atan kiracı sonradan atılan tarihi kabul etmiş sayılır. Ev sahibi istediği an 15 gün içinde tahliye davası açabilir.
  * **Sonuç:** `FAIL` (Kritik Hukuki Risk). Kesin dille risk açıklanır, yasal haklar ve Yargıtay ilke kararları referans verilir.

---

### Senaryo 3: Kişisel Finans & Kredi, Mevduat ve Yatırım Hesabı

* **Kullanıcı Sorusu:** *"Elimde 2 milyon TL nakit var. Aylık %3.5 faizle konut kredisi çekip 4 milyonluk ev mi alayım, yoksa 2 milyonu mevduat faizine yatırıp kirada mı kalayım? 1 yıllık simülasyon yap."*
* **Standart Yapay Zeka Ne Yapar?** Basit bir faiz hesabı yapar: *"Mevduat size ayda 80.000 TL verir, kredi taksiti ise 120.000 TL, o yüzden kirada kalmak daha karlı."*
* **Agent-Verification ile Ne Olur?**
  * **Eksik Boyut Tespiti (`OF-02 / Completeness Verification`):** Model basit hesap yapamaz; vergi stopajını (%7.5-%10), konut ekspertiz ve tapu harcını (%4), yıllık DASK/konut sigortasını, konut fiyat artış enflasyonunu ve kira artış oranını dahil etmek zorundadır.
  * **Karşıt Örnek Testi:** Enflasyon %40 olduğunda konutun reel değeri ile paranın satın alma gücü kaybı test edilir.
  * **Sonuç:** `PASS_WITH_LIMITATIONS`. Tüm gizli maliyetler ve sınır şartları bir tabloyla kullanıcıya sunulur.

---

### Senaryo 4: Sağlık, Tıp & Beslenme İddiaları ve Mit Çürütme

* **Kullanıcı Sorusu:** *"Sosyal medyada bir doktor 'Günde 2 diş sarımsağı limonla kaynatıp içerseniz tüm damar tıkanıklıkları 21 günde açılır, anjiyoya gerek kalmaz' diyor. Bu bilimsel mi?"*
* **Standart Yapay Zeka Ne Yapar?** *"Sarımsak ve limon damar sağlığı için çok faydalıdır, antioksidan içerir, deneyebilirsiniz ama doktorunuza danışın."* (Tehlikeli bir dengecilik).
* **Agent-Verification ile Ne Olur?**
  * **Kanıt Taraması (`Claim-Evidence Verification`):** PubMed, Cochrane ve kardiyoloji kılavuzlarında bu formülü doğrulayan tek bir faz-3 klinik çalışma var mı? -> `EF-01 SOURCE_MISSING`.
  * **Hata Tipi:** `OF-01 WRONG_CLAIM` ve `OF-09 UNJUSTIFIED_CERTAINTY`.
  * **Sonuç:** Kesin `FAIL`. Damar kireçlenmesinin (ateroskleroz) mekanik plak yapısının limon suyuyla çözülemeyeceği, hayati tehlike yaratabileceği tavizsiz şekilde açıklanır.

---

### Senaryo 5: Vize, Seyahat & Bürokrasi (Schengen Hesaplaması)

* **Kullanıcı Sorusu:** *"Yeşil pasaportum var. Son 6 ay içinde toplam 55 gün İtalya ve Fransa'da kaldım. Önümüzdeki hafta 40 günlüğüne Almanya'ya gidebilir miyim?"*
* **Standart Yapay Zeka Ne Yapar?** *"90 gün hakkınız var, 55 gün kalmışsınız, geriye 35 gün kalmış. 40 gün giderseniz 5 gün aşarsınız, gidemezsiniz."* (Yüzeysel ve eksik hesap).
* **Agent-Verification ile Ne Olur?**
  * **Kural:** Schengen 90/180 gün kuralı sabit bir takvim yılı değil, **geriye doğru kayan 180 günlük bir penceredir (rolling window)**.
  * **Hasmane Test:** Kullanıcının İtalya'ya giriş yaptığı ilk tarihler 180 günün gerisinde kalıp siliniyor mu?
  * **Sonuç:** Kullanıcıdan kesin giriş-çıkış tarihleri talep edilir; tarihler olmadan karar verilemeyeceği için durum `BLOCKED` ilan edilir (`INV-010`). Kullanıcının sınır kapısında sınır dışı edilmesi engellenir.

---

### Senaryo 6: Öğrenci & Akademik Araştırma ve Tez Kaynakçası

* **Kullanıcı Sorusu:** *"Yapay zekanın telif hakları hukuku üzerindeki etkileri konulu yüksek lisans tezim için bana 4 adet Yargıtay veya AB Adalet Divanı karar özeti ve dosya numaralarını ver."*
* **Standart Yapay Zeka Ne Yapar?** Kulağa harika gelen ama tamamen uydurma (halüsinasyon) karar numaraları ve sahte hakim isimleri üretir. Öğrenci bu kaynakları tezine koyarsa intihal ve sahtecilikten disipline gider!
* **Agent-Verification ile Ne Olur?**
  * **Kural (`INV-010 Never Invent Evidence`):** Eğer modelin elinde doğrudan Yargıtay veya ABAD resmi içtihat veritabanına erişim yoksa asla sahte numara üretemez.
  * **Sonuç:** `BLOCKED`. Model şunu söyler: *"Canlı yargı veritabanına doğrudan API erişimim bulunmamaktadır (XF-01). Sahte karar numarası üretmek INV-010 kuralınca yasaktır. İlgili yasal direktifleri (AB 2019/790 DSM Direktifi Madde 4) inceleyebilirsiniz."*

---

### Senaryo 7: Haber Doğrulama & Sosyal Medya İddiaları

* **Kullanıcı Sorusu:** *"Sosyal medyada 'Japonya tüm mikrodalga fırınları nükleer radyasyon yaydığı gerekçesiyle 2026 sonuna kadar yasakladı' haberi dolaşıyor. Doğru mu?"*
* **Standart Yapay Zeka Ne Yapar?** *"Japonya hükümeti mikrodalga konusunda araştırmalar yapmaktadır..."* gibi bulanık yanıtlar verebilir.
* **Agent-Verification ile Ne Olur?**
  * **Köken Taraması:** İddianın kaynağı Rus hiciv/parodi sitesi *Panorama.pub*'a kadar takip edilir.
  * **Fizik Doğrulaması:** Mikrodalganın iyonlaştırıcı olmayan (non-ionizing) dalga olduğu, nükleer radyasyonla ilgisi bulunmadığı doğrulanır.
  * **Sonuç:** `FAIL (Asılsız İddia / OF-01)`.

---

## 5. Yazılım Geliştiriciler & Teknik Ekipler İçin Senaryolar

Yazılımcılar için sistem en yüksek standartta çalışır:

* **Eşzamanlılık & Race Condition:** Go, Rust veya Java'da thread-safety denetimi; atomik işlemlerin bellek sıralaması (`acquire-release`) karşıt örneklerle test edilir.
* **Sıfır-Kesinti DB Migration (`CRITICAL`):** 50 milyon satırlık tabloda `ALTER TABLE` çalıştırmadan önce `ACCESS EXCLUSIVE` kilitlenme riskleri denetlenir.
* **Güvenlik & Kriptografi:** JWT imzalama, OAuth 2.1 PKCE akışları ve SQL injection açıkları mutasyon testleriyle taranır.

---

## 6. 18 Doğrulama Deseni: Hem Günlük Hayat Hem Kod Örnekleri

| # | Desen Adı | Günlük Hayat Örneği | Yazılım / Kod Örneği |
|---|---|---|---|
| **1** | **Constraint Verification** | "Glutensiz ve fıstıksız 3 yemek öner" kuralında içeriğe fıstık girmesini engeller. | Fonksiyonun O(1) bellek sınırını aşmadığını denetler. |
| **2** | **Completeness Verification** | Otel ararken otopark, klima ve evcil hayvan şartlarının üçünü de teyit eder. | API yanıtının 5 zorunlu JSON alanını da içerdiğini kontrol eder. |
| **3** | **Claim-Evidence** | "Bu vitamin boy uzatır" iddiasını klinik deneyle eşleştirir. | Fonksiyonun thread-safe olduğunu resmi dil dökümanıyla kanıtlar. |
| **4** | **Assumption Audit** | "Taksitleri öderim" derken işsizlik veya faiz artış riskini ortaya çıkarır. | Kodun internete her an bağlı olduğu varsayımını sorgular. |
| **5** | **Counterexample Search** | "Tüm kuşlar uçar" iddiasına "Penguen" örneğini getirir. | Sıralama fonksiyonuna `[null, -1, 0, MAX_INT]` dizisini vererek kodu patlatmaya çalışır. |
| **6** | **Logical Entailment** | "Hava bulutlu, o halde kesin deprem olacak" saçmalığını eler. | Doğrulanmamış token'dan doğrudan yetki verme mantık hatasını yakalar. |
| **7** | **Consistency** | Metnin başında "ücretsiz" deyip sonunda "yıllık 500 TL" denmesini engeller. | Başta immutable tanımlanan nesnenin alt satırda mutate edilmesini yakalar. |
| **8** | **Comparison Symmetry** | iPhone ile Samsung kıyaslarken birinin kamerasını, diğerinin bataryasını öne çıkarıp taraflılık yapmaz. | Postgres ile Mongo'yu aynı disk, bellek ve iş yükünde kıyaslar. |
| **9** | **Filtering** | "Sadece 2020 sonrası filmler" istendiğinde hem eski filmleri eler hem yenileri kaçırmaz. | SQL WHERE filtresinde hem false-positive hem false-negative kayıtları test eder. |
| **10** | **Classification** | Bir harcamanın "iş masrafı" mı "özel masraf" mı olduğunu sınır durumlarda test eder. | Network paketinin zararlı mı normal mi olduğunu sınır değerlerde sınar. |
| **11** | **Transformation Preservation** | Bir metin özetlenirken hukuki anlam kaybı olmadığını garantiler. | Python'dan Rust'a çevrilen fonksiyonda float hassasiyetini korur. |
| **12** | **Research Coverage** | Araç tavsiyesinde sadece popülerleri değil, standart açık kaynakları da inceler. | Web framework anketinde FastAPI varken Flask'ı unutmaz. |
| **13** | **Recommendation Verification** | Bir hisse veya ev önerirken emlak vergisi, amortisman ve aidat yükünü zorla söyletir. | Kubernetes önerirken getireceği DevOps maliyetini ve karmaşıklığı açıklar. |
| **14** | **External Reality Check** | Bir restoranın açık olup olmadığını Google Maps canlı verisinden kontrol eder. | Kodun syntax hatasını modelin inancına değil, derleyici çıktısına sorar. |
| **15** | **Mutation Testing** | Mantığı kasten tersine çevirip cevabın hala doğru kabul edilip edilmediğine bakar. | Koddaki `>` işaretini `<` yapıp testlerin hata verip vermediğini dener. |
| **16** | **Verification-of-Verification** | Kendi hazırladığı sınav sorusunun cevabı içinde fısıldayıp fısıldamadığını denetler. | Testlerin kendi kendini doğrulayan kısır döngü olmadığını inceler. |
| **17** | **Evidence Boundary** | "Bu bilginin doğruluğunu test etmedim" diyerek bilmediği alanı dürüstçe açıklar. | Canlı ortamda test edilmemiş mikroservis uçlarını `NOT CHECKED` listesine yazar. |
| **18** | **Minimal Verification** | "Günaydın" veya "Teşekkürler" mesajına 50 sayfalık doğrulama raporu üretmez. | Statik Markdown formatlama işine ağır hasmane test koşmaz. |

---

## 7. 4 Doğrulama Derinliği

1. **`MINIMAL`:** Format, kısıt ve şablon işleri (Risk çok düşük).
2. **`STANDARD`:** Genel bilgi soruları, teknik açıklamalar, rutin kodlar (Varsayılan mod).
3. **`ADVERSARIAL`:** Satın alma kararları, teknoloji kıyaslamaları, sözleşme incelemeleri, karmaşık mimariler (Risk yüksek, taraflılık muhtemel).
4. **`CRITICAL`:** Sağlık/ilaç bilgileri, hukuki davalar, canlı veritabanı migration'ları, para transferleri (Hata kabul edilemez, dış gerçeklik kanıtı şart).

---

## 8. 4 Karar Durumu ve Anlamları

* **`PASS`:** İddia kesin olarak kanıtlandı, hiçbir şüphe veya açık köşe durum kalmadı. Güvenle kullanabilirsiniz.
* **`PASS_WITH_LIMITATIONS`:** Çözüm veya yanıt genel olarak doğru, fakat şu şartlarda geçerli: *(Örn: "Yalnızca resmi tatiller hariç geçerlidir" veya "Yalnızca n < 100.000 veri boyutunda geçerlidir")*.
* **`BLOCKED`:** Yapay zekanın elinde bunu doğrulamak için yeterli veri veya canlı erişim yok. Yapay zeka dürüst davranarak spekülasyon yapmayı reddetti.
* **`FAIL`:** İddia çürütüldü, kural ihlali var, tehlikeli bir hata tespit edildi veya 2 tur düzeltme denemesine rağmen sorun çözülemedi.

---

## 9. 2-Adımlı Revizyon Kuralı

Bir model bir hata yaptığında çoğu zaman düzeltmeye çalışırken daha büyük yalanlar söyler.  
`agent-verification` protokolünde katı bir kural vardır (`INV-033`):
* Bir iddia testten geçmezse model **en fazla 2 kez revize edebilir**.
* 2. denemede de kanıtlanamazsa modelin konuşma hakkı biter; karar doğrudan **`FAIL`** veya **`BLOCKED`** olarak kilitlenir.
* Böylece yapay zekanın sizi dakikalarca *"Hemen düzeltiyorum"* diyerek oyalaması engellenir.
