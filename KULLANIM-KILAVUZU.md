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
10. [Yapay Zekanın Çalışmasını İzlemek: Canlı Doğrulama İzi](#10-yapay-zekanın-çalışmasını-i̇zlemek-canlı-doğrulama-i̇zi)

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

### Senaryo 8: Girişimcilik & Startup (Pazar Büyüklüğü TAM/SAM/SOM Denetimi)

* **Kullanıcı Sorusu:** *"Evcil hayvanlar için GPS'li akıllı tasma üreten bir girişimim var. Yatırımcı sunumunda Türkiye pazar büyüklüğünü (TAM) 5 milyar dolar yazdım. Bu rakam inandırıcı mı?"*
* **Standart Yapay Zeka Ne Yapar?** *"Evcil hayvan sektörü hızla büyüyor, Türkiye'de milyonlarca hayvan var, harika bir pazar fırsatı!"* (Yatırımcı önünde kurucuyu rezil edecek bir teyitsiz onay).
* **Agent-Verification ile Ne Olur?**
  * **İddia-Kanıt Çapraz Sorgusu (`Claim-Evidence`):** Türkiye'deki resmi veteriner ve çipli kayıtlı evcil kedi/köpek sayısı yaklaşık 6-8 milyondur. Akıllı tasma ortalama perakende satış fiyatı 40-50 dolardır.
  * **Hasmane Sınır Testi (`Counterexample Search`):** Türkiye'deki **tüm** kedi ve köpek sahipleri bu tasmayı satın alsa dahi pazar tavanı 300-400 milyon doları geçemez. 5 milyar dolar iddiası 12 kat şişirilmiştir.
  * **Hata Tipi:** `OF-01 (WRONG_CLAIM)` ve `OF-09 (UNJUSTIFIED_CERTAINTY)`.
  * **Sonuç:** `FAIL`. Model şişirilmiş rakamı reddeder, girişimciye gerçekçi bir SAM/SOM hesaplama modeli sunar.

---

### Senaryo 9: İnsan Kaynakları & Kariyer (İş Teklifi ve Hisse Opsiyonu Kıyaslaması)

* **Kullanıcı Sorusu:** *"A Şirketi 120.000 TL net maaş veriyor. B Şirketi ise 85.000 TL net maaş + 4 yılda hak kazanılacak 50.000 $ değerinde hisse opsiyonu (ESOP/hisse hakkı) teklif ediyor. Hangisi daha avantajlı?"*
* **Standart Yapay Zeka Ne Yapar?** Basit matematik yapar: 50.000$ / 4 yıl = 12.500$/yıl. Bunu aylık maaşa ekleyip B şirketini daha karlı ilan eder.
* **Agent-Verification ile Ne Olur?**
  * **Varsayım Denetimi (`Assumption Audit`):** B şirketi halka açık bir şirket mi? Halka açık değilse hisseler likit değildir; bir satış/IPO olmadan paraya çevrilemez (`UNVERIFIED`).
  * **Gizli Şart Denetimi:** 1 yıllık "cliff" süresi var mıdır? Çalışan 11. ayda ayrılırsa hisse hakkı sıfır kalır mı? İleriki yatırım turlarında sulandırma (dilution) riski nedir?
  * **Sonuç:** `PASS_WITH_LIMITATIONS`. B şirketinin teklifindeki nakit akışı riskleri ve sınır şartları net bir tabloyla raporlanır.

---

### Senaryo 10: Ev Tadilatı, Usta Teklifleri ve Gizli Maliyetler

* **Kullanıcı Sorusu:** *"120 m² dairem için bir usta '400.000 TL anahtar teslim komple banyo, mutfak ve zemin yenilerim' dedi. Bu bütçe yeterli mi, nerede yanılabilirim?"*
* **Standart Yapay Zeka Ne Yapar?** *"Evet, ortalama olarak 400 bin TL tadilat için makul bir fiyattır, ustanıza güvenebilirsiniz."*
* **Agent-Verification ile Ne Olur?**
  * **Eksiksizlik Denetimi (`Completeness Verification`):** Moloz atımı ve belediye çöp konteyner bedeli fiyata dahil mi? Eski tesisat borularındaki paslanma çıktığında kırılacak ek duvarların masrafı kime ait? Armatür ve seramikler 1. sınıf mı yoksa çıplak işçilik mi? KDV dahil mi?
  * **Sonuç:** `PASS_WITH_LIMITATIONS`. Kullanıcının önüne ustaya imzalatması gereken 14 maddelik bağlayıcı şartname maddesi konur.

---

### Senaryo 11: Otomotiv & İkinci El Araç Ekspertiz Raporu Analizi

* **Kullanıcı Sorusu:** *"Satıcı aracın 'Sadece sol ön çamurluğu boyalı, tramer kaydı 65.000 TL' olduğunu söylüyor. Ekspertiz raporunu nasıl okumalıyım?"*
* **Standart Yapay Zeka Ne Yapar?** *"Çamurluk boyası önemsizdir, güvenle alabilirsiniz."*
* **Agent-Verification ile Ne Olur?**
  * **Tutarlılık Denetimi (`Consistency Verification`):** Tek bir saç çamurluğun boya işçiliği tramerde 65.000 TL çıkaramaz.
  * **Karşıt İddia Taraması:** Bu hasar rakamı; LED far kırılması, tampon demiri değişimi, radyatör paneli veya podye/şasi ezilmesine işaret eder.
  * **Sonuç:** `PASS_WITH_LIMITATIONS`. Alıcıya doğrudan şasi ucu, airbag soketleri ve ön panel vidalarının kontrol edilmesi talimatı verilir.

---

### Senaryo 12: Eğitim & Sınav Sorusu Hazırlama (Öğretmenler İçin)

* **Kullanıcı Sorusu:** *"Kimya dersinde 'Kimyasal Denge ve Le Chatelier İlkesi' konusunda üniversite sınavına yönelik zor bir çoktan seçmeli soru ve 5 şık hazırla."*
* **Standart Yapay Zeka Ne Yapar?** Soru kökünde cevabı farkında olmadan fısıldar veya şıkların ikisini birbiriyle çelişkili/iki doğru cevaplı hale getirir.
* **Agent-Verification ile Ne Olur?**
  * **Doğrulamanın Doğrulanması (`Verification-of-Verification / Pattern 16`):** Soru kökü bağımsız olarak test edilir; soru metninde cevabı ima eden döngüsel bir ipucu var mı (`VF-03`)?
  * **Çeldirici Denetimi:** Yanlış şıklar öğrencilerin en tipik kavram yanılgılarını (örn: katıların dengeye etkisi) hedefliyor mu?
  * **Sonuç:** `PASS`. Sorunun tek ve kesin bir cevabı olduğu mekanik olarak kanıtlanır.

---

### Senaryo 13: E-Ticaret, Dropshipping & Reklam Kampanyası ROI Gerçekliği

* **Kullanıcı Sorusu:** *"TikTok'tan bulduğum bir ürünü 4$'a alıp 25$'a satacağım. Reklam maliyetim satış başına 8$ olursa, günlük 20 satışta ayda 7.800$ net kar edebilir miyim?"*
* **Standart Yapay Zeka Ne Yapar?** 25 - 4 - 8 = 13$ kar. 13 x 20 x 30 = 7.800$. *"Tebrikler, harika bir kazanç!"* der.
* **Agent-Verification ile Ne Olur?**
  * **Kapsam ve Eksik Masraf Denetimi (`OF-02 / OF-05`):** Ödeme altyapısı komisyonu (%3.5 + 0.30$), kargo ve gümrük masrafları, e-ticaret platform aboneliği, ortalama %15 iade oranı (chargeback ve kırık ürün), vergi stopajı hesaba katılmamıştır.
  * **Hasmane Simülasyon:** %15 iade ve kargo zararı eklendiğinde gerçek karın sıfıra yaklaştığı veya eksiye düştüğü somut matematiksel tabloyla gösterilir.
  * **Sonuç:** `FAIL (Gerçek Dışı Bütçe)`.

---

### Senaryo 14: Yaratıcı Yazarlık & Senaryo Mantık Tutarlılığı (Plot Holes)

* **Kullanıcı Sorusu:** *"Dedektif romanımda katil, kurbanı gece 23:00'da kilitli bir odada zehirliyor. Aynı katil saat 23:15'te 50 km uzaktaki bir restoranda kamera kaydıyla alibi (mazeret) üretiyor. Kurgum tutarlı mı?"*
* **Standart Yapay Zeka Ne Yapar?** *"Çok heyecanlı bir kurgu, harika bir gizem!"* der.
* **Agent-Verification ile Ne Olur?**
  * **Fizik ve Mantık Denetimi (`Logical Entailment`):** Gece 23:00 ile 23:15 arasında 15 dakika vardır. 50 km mesafeyi 15 dakikada katetmek için katilin ortalama 200 km/s hızla hiç durmadan gitmesi gerekir. Şehir içi trafikte bu imkansızdır.
  * **Çözüm:** Model katilin cinayet saatini geciktiren bir mekanizma (örn: gecikmeli salınan zehir veya buz kalıbı) kurmasını önererek senaryodaki mantık deliğini onarır.
  * **Sonuç:** `PASS_WITH_LIMITATIONS`.

---

### Senaryo 15: Mutfak & Gastronomi (Kimyasal Reaksiyon ve Gıda Güvenliği)

* **Kullanıcı Sorusu:** *"Tavuk göğsünü 54 derecede 35 dakika sous-vide (vakumda) pişirsem misafirlerime güvenle ikram edebilir miyim?"*
* **Standart Yapay Zeka Ne Yapar?** *"Sous-vide ile tavuk çok sulu ve lezzetli olur, 54 derece denenebilir."* (Ağır gıda zehirlenmesi riski!).
* **Agent-Verification ile Ne Olur?**
  * **Risk Seviyesi:** `CRITICAL Derinlik`.
  * **Dış Gerçeklik ve Sağlık Kılavuzu Denetimi (`External Reality Check`):** USDA ve FDA gıda güvenliği pastörizasyon tablolarına göre, tavukta *Salmonella* ve *Listeria* bakterilerinin log-7 seviyesinde yok edilmesi için 54°C sıcaklıkta etin merkezinin kesintisiz en az **112 dakika** tutulması zorunludur. 35 dakika süre kesinlikle ölümcül patojenleri öldürmez.
  * **Sonuç:** Kesin `FAIL`. Misafirlere servis edilmesi engellenir, doğru pastörizasyon süre/derece tablosu verilir.

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

---

## 10. Yapay Zekanın Çalışmasını İzlemek: Canlı Doğrulama İzi

İzleyemediğiniz bir doğrulama, gerçekten yapılmış mı yoksa yapılmamış mı olduğunu ayırt edemeyeceğiniz bir doğrulamadır. Bu yüzden protokol, işi bitince yazılmış derli toplu bir özet yerine **çalışırken** anlatır: her aşamaya girerken, o aşamanın işi başlamadan önce kısa bir güncelleme gönderir.

### Ekranda ne görürsünüz?

```text
🛡️ Doğrulama · ADVERSARIAL · 1/8 · derinlik
Yüksek etkili satın alma kararı, kaynaklar çelişkili. ADVERSARIAL yürütülüyor:
gizli maliyet denetimi, karşıt örnekler ve simetrik karşılaştırma.

🛡️ Doğrulama · ADVERSARIAL · 4/8 · testler
7 test tanımlandı. 6'sı geçti; TEST-004 başarısız (OF-05): alıntılanan batarya ölçümü
25°C'de yapılmış, oysa CL-002 sürekli yük iddia ediyor.

🛡️ Doğrulama · ADVERSARIAL · 5/8 · revizyon
CL-002 "hafif yük" olarak daraltıldı; TEST-004 geçersiz sayıldı, eski sonuç artık sayılmıyor.

🛡️ Doğrulama · ADVERSARIAL · 6/8 · yeniden test
TEST-005, revize edilen iddia üzerinde yeniden koşuldu → PASS.

🛡️ Doğrulama · ADVERSARIAL · 7/8 · saldırı
4 saatlik render karşıt örneği: frekans %45 düşüyor. TEST-007 (soğutma) eklendi;
ultrabook'ta başarısız oldu — sınır gizlenmedi, doğrulandı.

⚠️ PASS_WITH_LIMITATIONS · ADVERSARIAL · LIVE
Kritik iddialar: 3/3 doğrulandı · Testler: 7/8 geçti (TEST-007 başarısız, açıklandı) · Revizyon: 1
Sınırlar: CL-002 yalnızca hafif yük için geçerli; TEST-007 (soğutma) ultrabook'ta başarısız oldu.
[claims=3/3, tests=7/8, rev=1]
```

### Bu neden sonuçtan daha önemli?

* **İtiraz edebileceğiniz an, iş sürerken.** Yapay zeka yanlış derinliği seçtiyse, soruyu yanlış anladıysa veya sizin için önemli bir kaynağı atladıysa, bunu 2. aşamada görürsünüz — kendinden emin bir cevap kararınızı çoktan çelmişken değil.
* **Başarısız kontroller görünür kalır.** Hatasını sessizce düzelten bir ajan, ilk seferde doğru yapan bir ajandan dışarıdan ayırt edilemez. *Neyin başarısız olduğunu ve neyin değiştiğini* görmek, güven ile kör güven arasındaki farktır.
* **Sınırlar kanıta bağlı gelir.** Karar kartındaki sınır, sözleşmedeki kayıtla aynıdır; böylece uyarı özetten sessizce kaybolamaz.

### Detay seviyesini siz belirlersiniz

| Ne dersiniz? | Ne alırsınız? |
|---|---|
| *(hiçbir şey)* | `concise`: her aşama için kısa bir satır + karar kartı |
| *"Her adımı göster / hangi kontrolleri yaptın?"* | `detailed`: test kimlikleri, gözlemler, kanıt kimlikleri |
| *"Sadece cevabı ver"* | `silent`: açılış satırı + karar kartı — iz yine kaydedilir, sadece yazdırılmaz |

Doğrudan talep etmek için sorunuzun sonuna şunu ekleyin:

```text
[agent-verification ile doğrula ve her adımı canlı göster: seçilen derinlik,
iddialar, testler, başarısız kontroller, revizyonlar ve karar — sadece sonuç değil.]
```

### Yapay zeka sessizleşirse

Sessizlik bir üslup değil, hatadır. Şunu sorun: *"Hangi doğrulama aşamasındasın, şu ana kadar neyi kontrol ettin ve ne başarısız oldu?"* Arayüz gerçekten canlı akış desteklemiyorsa (tek yanıtlı API, toplu iş) ajan bunu söylemek ve `TRACE_DEFERRED` sınırlamasını açıklamak zorundadır — uydurma bir "canlı" günlük, dürüst bir özetten daha kötüdür.

### Kart da denetlenir

Karar kartı serbest metin değildir. Her sayı sözleşmeden türetilir (`INV-059`): kritik iddialar `claims[]`'ten, testler terminal `tests[]`'ten, revizyonlar `revisions[]`'ten, sınırlar `disclosed_limitations[]`'ten. "8/8 test geçti" yazıp altı test koştuysanız bu yuvarlama değil, `VF-10`'dur.

Kartın sabit ve denetlenebilir bir biçimi vardır. Kart çizilmeden önce tanımlanan her test bitmiş olmalıdır (`INV-068`); yarım kalan bir test "7/8" paydasından sessizce düşemez. İlk satır her zaman işaret, karar, derinlik ve `LIVE`/`RETRO` durumudur (`INV-069`); son satır `[claims=…, tests=…, rev=…]` altbilgisidir. Etiket de kanıtıyla eşleşmelidir (`INV-070`): açık sınırı veya hatası olan bir `PASS` yanlış etiketlenmiştir, hiç sınırı olmayan bir `PASS_WITH_LIMITATIONS` de aynı şekilde yanlıştır; `BLOCKED` veya `FAIL` kartı engelini ya da açık hata kimliklerini göstermek zorundadır. İz ayrıca temiz kapanmalı (`INV-060`) ve kullanmadığı bir canlı akış yeteneğini iddia etmemelidir (`INV-061`).

### Varsayımlar ve derinlik düşürmeler de görünürdür

Doğrulanmış görünüp doğrulanmamış olmanın iki sessiz yolu burada kapatılır. Birincisi, bir varsayım sadece beyan edilerek "doğrulandı" yapılamaz (`INV-071`): onu gerçekten kapsayan kanıt gerekir; kritik bir varsayım için harici kaynak ya da gözlemlenmiş bir kontrol şarttır. İkincisi, sonucu sınırlayan koşul sözleşmenin görebileceği yerde adlandırılmalıdır — sınırlar (veya engeller) listesinde bir `AS-XXX` referansı (`INV-072`) — metin arasında geçen bir cümle değil. Bir kontrol koşulamadığı için ajan derinliği düşürmek zorunda kalırsa, bu yönlü bir *derinlik düşürmesidir*: neyin kontrol edilmekten çıktığını söylemeli ve bir `DOWNGRADE` referansı taşımalıdır (`INV-073`); böylece geri çekilme, ekstra titizlik gibi okunamaz.

### Beyan, kayıt yerine geçmez

Ajanın eskiden sadece *iddia edebildiği* üç şey artık *kaydediliyor*. Karar öncesi kontrol listesi kutu kutu bir kayıttır (`INV-074`): "tüm kutular işaretli" ancak her kutu ya yapıldı olarak ya da — uygulanmıyorsa — gerekçesiyle listelendiğinde kabul edilir. Bir kabul koşulunu farklı bir kontrol ailesiyle karşılayan test, gerekçesiyle istisna olarak bildirilmelidir (`INV-075`); böylece "belgelenmiş eşleme" "bana güven" anlamına gelemez. Ve *doğrulandı* işaretli bir iddia, **bu koşuda** gözlemlenen kanıta dayanmalıdır (`INV-076`); eski, önbellekten gelen kanıt cevaba katkı verebilir ama o iddiayı "destekleniyor" seviyesinde sınırlar ve açıklanmak zorundadır. Üç durumda da metin yetmez — sözleşmenin kaydı göstermesi gerekir.

Aynı fikir, sistemin gerçeği kontrol etmeden kendini "doğrulamasının" üç yolunu da kapatır. Bir test neyle karşılaştırdığını bildirmek zorundadır: yalnızca cevabı kendi öncülleriyle karşılaştıran ya da aynı iddianın yeniden yazımını okuyan bir kontrol doğrulama değildir (`INV-077`). Bir onarım kapsam değişimini göstermelidir: düzeltmesi gereken başarısızlığı sessizce yumuşatmak ya da bir kabul koşulunu düşürmek onarım değildir (`INV-078`). Ve kanıtın bağımsız bir kaynağı olmalıdır: tek "kaynak" cevabın kendisiyse, iddia en fazla desteklenmiş sayılır, asla doğrulanmış değil (`INV-079`).

### Defter tutma da denetlenir

Üç sayı ve liste eskiden kendi beyanına dayanıyordu. Revizyon deneme sayacı artık her iddia için revizyon geçmişinden **hesaplanır** (`INV-080`); böylece ajan sonsuza kadar yamamak ya da iki deneme sınırını aşmak için sayacı sıfırlayamaz — yalnızca sayaç sıfırlandığı için ayakta kalan bir PASS geçersizdir. İddia edilen derinlik bir **adım kaydıyla** desteklenir (`INV-081`): o seviyenin numaralı her adımı, kanıtlayan iz veya esere işaret ederek "yapıldı" ya da gerekçesiyle "uygulanmıyor" olarak listelenir. Gerekçe taşıyan metin alanları da (sınır neden geçerli, engeli ne kaldırır, aile istisnası neden sağlam) gerçekten bir şey söylemek zorundadır (`INV-082`): "N/A", "-" ya da alan adının tekrarı gerekçe değildir.

### Boş kapsamlar ve çelişen etiketler

Kesin görünmenin iki yolu daha. Birincisi kapsamlar: bir iddianın ya da kaynağın belirtilen kapsamı boşsa ya da sadece "tümü" ise, "dar kanıt, geniş iddia" kontrolünün karşılaştıracak bir şeyi kalmaz ve o iddia varsayılan olarak geçer (`INV-083`). İkincisi birbiriyle çelişen etiketler: bir atıf, kaynak türü olarak yerel bir dosyayı gösterirken harici köken iddia edemez; bir test yalnızca cevabın iç tutarlılığını kontrol ederken kendini harici sayamaz (`INV-084`). Ve adım kaydı, o adımları gerçekten gösteren iz girdilerine işaret etmelidir — yalnızca son duyuruyu göstermek kapsama değildir (`INV-085`).

### Şiddet, çürütücü girdi ve hiçbir şey söylemeyen cümleler

Değerli görünüp hiçbir şey taşımayan üç yer daha. Bir başarısızlığın şiddeti artık düzenlenebilir bir alan değil, bir *geçmiş*: yalnızca onu değiştiren revizyon üzerinden hareket edebilir; eski ve yeni değer, gerekçe ve — şiddet düşürülüyorsa — bulgunun gerçekten daraldığını gösteren taze bir gözlem kaydedilir (`INV-086`). Ayrıca çözülmemiş `MAJOR` veya `CRITICAL` bir bulgu nihai kararı sınırlar (`MAJOR` `PASS_WITH_LIMITATIONS`'ta, `CRITICAL` `FAIL`/`BLOCKED`'ta); yani ibreyi aşağı çevirmek temiz bir PASS'e giden yol değildir. Kritik bir test, yakalayacağı yanlış girdiyi adlandırmalıdır — "yanlış bir cevap" değil, yanındaki testle aynı cümle de değil (`INV-087`); tek yanlış cevabı "bir şeyler yanlış" olan test bir eşik koymamıştır. Ve izlediğiniz ilerleme satırları ne üzerinde çalıştığını söylemelidir (`INV-088`): on iki tane "Kontrol ediliyor." gerçek kimliklere çözülebilir ama size hiçbir şey anlatmaz; her özet kendi birimini adlandırır.

### İzde asla görünmemesi gerekenler

API anahtarı, parola, token, oturum kimliği veya kişisel veri yok — bunun yerine `EV-*` kimliği ya da dosya yolu kullanılır (`INV-062`). Her güncelleme 280 karakterin altındadır ve güncelleme sayısı derinliğe göre sınırlıdır; böylece şeffaflık log duvarına dönüşmez.

### Hikâyenin sırası da denetlenir

İz doğru olsa bile sırası yanıltıcı olabilir: hiç test koşmadan ATTACK, denetimden önce DECISION demek `VF-09`'dur (`INV-063`). Her aşama kendi kanıtını göstermelidir — başarısızlık için `F-*`, revizyon için `REV-*`, yeniden test için koşulmuş `TEST-*`, CRITICAL için external/mutation testi (`INV-064`). Bir adım bir dakikadan uzun sürerse sessizlik değil, "hâlâ çalışıyor, henüz sonuç yok" nabzı beklenir.

### Kart, koşunun ne kadar titiz ve ne kadar canlı olduğunu söyler

Kart ayrıca kaynağını bildirir: yürütülen derinlik ve izin `LIVE` mi `RETRO` mu olduğu (`INV-066`). İz de o derinlik için eksiksiz olmalıdır — açılış `DEPTH`, gereken aşamalar ve her başarısızlık/revizyon/yükseltme için bir kayıt (`INV-065`); kısa ve cilalı bir iz `VF-09`'dur, düzenli bir özet değil. Kartın metni ayrıca `[claims=..., tests=..., rev=...]` biçiminde kanonik bir altbilgi taşır ve bu değerler alanlarla eşleşmelidir (`INV-067`) — okuduğunuz sayılar sözleşmeden kopamaz.

### Makinece denetlenen taraf

* `INV-057` — iz, derinliğin gerektirdiği sıklıkta canlı akmalıdır; sonradan tek seferde yazılan iz `VF-09`'dur ve `PASS`'i engeller.
* `INV-058` — her güncelleme gerçek sözleşme kimliklerine ve sonuçlarına dayanmalı; karar kartı ile nihai karar birbirini tutmalıdır.
* `INV-059`–`INV-062` — kart türetilmiş olmalı (`VF-10`), iz kapalı olmalı, erteleme dürüst olmalı, içerik gizlenmiş ve sınırlı olmalı (`VF-09`).
* `INV-063`–`INV-064` — hikâye yaşam döngüsü sırasıyla anlatılmalı ve her aşama kendi kanıtını göstermeli (`VF-09`).
* `INV-065`–`INV-066` — iz derinlik için eksiksiz olmalı ve kart derinlik + `LIVE`/`RETRO` göstermeli (`VF-09`/`VF-10`).
* `INV-067` — kartın metnindeki sayılar ve kanonik altbilgi alanlarla eşleşmeli (`VF-10`).
* `INV-068`–`INV-070` — tanımlanan hiçbir test yarım bırakılamaz (`VF-06`); kart kanonik işaret/karar/derinlik/iz başlığıyla açılıp altbilgiyle kapanmalı; etiket kendi sınırları, engelleri veya açık hatalarıyla eşleşmelidir (`VF-10`).
* `INV-071`–`INV-073` — `VERIFIED` bir varsayım gerçek ve karşılıklı kanıta dayanmalıdır (`EF-01`/`VF-07`); kritik koşullar sınırlarda ya da engellerde `AS-XXX` ile adlandırılmalıdır (`VF-04`/`VF-06`); yükseltme/düşürme kayıtları yönlüdür (`VF-06`).
* `INV-074`–`INV-076` — kontrol listesi, kapanış bayrağının arkasında kutu kutu bir kayıttır (`VF-06`); uyuşmayan test ailesi istisna olarak bildirilmelidir (`VF-04`); `VERIFIED` iddialar önbellek değil bu koşunun kanıtını gerektirir (`EF-03`).
* `INV-077`–`INV-079` — kritik test gerçek dayanak bildirmelidir (`VF-03`); revizyon neyi düşürdüğünü/daralttığını kaydetmelidir (`VF-07`); ve bir iddia cevabın kendisine karşı doğrulanamaz (`EF-06`).
* `INV-080`–`INV-082` — deneme sayacı yazılmaz, türetilir (`VF-06`/`VF-07`); iddia edilen derinliğin her adımı kanıtıyla kaydedilir (`VF-06`); gerekçeler yer tutucu değil, gerçek olmalıdır (`VF-06`/`VF-04`).
* `INV-083`–`INV-085` — kapsamlar kaydedilmelidir ki eşleşme boşa düşmesin (`EF-04`); beyan çiftleri aynı eseri anlatmalıdır (`VF-06`); ve adım kaydı gerçekten sahip olduğu iz kapsamını göstermelidir (`VF-06`/`VF-09`).
* `INV-086`–`INV-088` — şiddet yalnızca kayıtlı ve kanıtlı bir revizyon farkıyla değişir, ciddi açık bulgu kararı sınırlar (`VF-06`/`VF-07`); kritik test somut bir yanlış girdi adlandırmalıdır (`VF-02`); ve her iz özeti anlattığı birimi adlandırmalıdır (`VF-09`).

Tam şartname: [`references/progress-protocol.md`](references/progress-protocol.md).
