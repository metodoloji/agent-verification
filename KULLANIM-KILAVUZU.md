# Agent Verification: Kapsamlı Kullanıcı Kılavuzu

[![Organization](https://img.shields.io/badge/org-metodoloji-0b7285?style=flat-square)](https://github.com/metodoloji)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE)
[![English Guide](https://img.shields.io/badge/guide-English-blue?style=flat-square)](USER-GUIDE.md)

> Bu kılavuz; `agent-verification` protokolünü tüm yönleriyle, 4 farklı derinlik seviyesini, 18 doğrulama desenini, hata taksonomisini ve uçtan uca gerçek hayat senaryolarını eksiksiz olarak öğrenip uygulayabilmeniz için hazırlanmıştır.

---

## 📑 İçindekiler

1. [Giriş: Neden Geleneksel Doğrulama Yetersizdir?](#1-giriş-neden-geleneksel-doğrulama-yetersizdir)
2. [Temel Çalışma Mantığı ve Yaşam Döngüsü](#2-temel-çalışma-mantığı-ve-yaşam-döngüsü)
3. [4 Doğrulama Derinliği ve Uygulama Senaryoları](#3-4-doğrulama-derinliği-ve-uygulama-senaryoları)
   - [MINIMAL: Biçim ve Kısıt Denetimi](#1-minimal-derinlik)
   - [STANDARD: Kod ve Bilgi Doğrulama](#2-standard-derinlik)
   - [ADVERSARIAL: Hasmane Saldırı ve Karşıt Örnekler](#3-adversarial-derinlik)
   - [CRITICAL: Üretim Düzeyi ve Dış Gerçeklik](#4-critical-derinlik)
4. [18 Doğrulama Deseni: Pratik Örnekler ve Promptlar](#4-18-doğrulama-deseni-pratik-örnekler-ve-promptlar)
5. [4 Karar Durumu ve Örnek Çıktılar (PASS, PWL, BLOCKED, FAIL)](#5-4-karar-durumu-ve-örnek-çıktılar)
6. [Hata Sınıflandırma ve 2-Adımlı Revizyon Kuralı](#6-hata-sınıflandırma-ve-2-adımlı-revizyon-kuralı)
7. [Farklı Roller İçin Prompt Şablonları](#7-farklı-roller-için-prompt-şablonları)
8. [Araç Entegrasyonları (Claude Code, Cursor, OpenHands)](#8-araç-entegrasyonları)

---

## 1. Giriş: Neden Geleneksel Doğrulama Yetersizdir?

Yapay zeka modellerine *"Cevabını kontrol et"*, *"Emin misin?"* veya *"Hata var mı bak"* dediğinizde genellikle şu gerçekleşir:
* **Yalancı Onaylama (Confirmation Bias):** Model kendi ürettiği metni baştan okur, kendi mantığına hayran kalır ve *"Evet, her şey doğru"* der (`VF-06 / VF-07`).
* **Halüsinatif Test:** Olmayan derleyicilerin veya veri tabanlarının çalıştığını iddia eder (`INV-010`).
* **Sonsuz Düzeltme Döngüsü:** Bir yeri düzeltirken başka bir yeri bozar ve hiçbir zaman kesin bir kanıta ulaşamaz (`VF-06`).

**`agent-verification` Ne Yapar?**  
Doğrulamayı bir temenni olmaktan çıkarıp **mekanik bir sözleşmeye (contract)** bağlar:
1. Yanıt baştan "doğrulanmamış aday" (`candidate output`) kabul edilir.
2. Çıktı atomik iddialara (`claims`) bölünür.
3. Her iddia için çürütmeye muktedir (`falsifiable`) testler üretilir.
4. Çürütülemeyen iddialar kanıtlanır; çürütülenler sınıflandırılıp revize edilir.

---

## 2. Temel Çalışma Mantığı ve Yaşam Döngüsü

Doğrulama akışı aşağıdaki adımları sırayla işletir:

```text
GÖREV (TASK)
  ↓
1. SÖZLEŞME TASLAĞI (Verification Contract taslağı çıkarılır)
  ↓
2. ADAY ÇIKTI (Model yanıtı üretir)
  ↓
3. İDDİA AYRIŞTIRMA (Çıktıdan CL-001, CL-002 gibi test edilebilir iddialar çıkarılır)
  ↓
4. TEST ÜRETİMİ (AC şartlarına uygun testler atanır)
  ↓
5. TEST ÇALIŞTIRMA (Kanıt ve gerçeklik üzerinde test edilir)
  ↓
  ├──> HATA VARSA: SINIFLANDIR (OF/VF/EF/XF) → REVİZE ET → YENİDEN TEST ET (Maksimum 2 tur)
  ↓
6. HASMANE SALDIRI (Adversarial Pass: Karşıt örnek ve uç durum araması)
  ↓
7. TESTLERİN DENETİMİ (Audit & Mental Mutation Testing)
  ↓
8. PRE-DECISION CHECKLIST (39 kapı kuralı denetlenir)
  ↓
NİHAİ KARAR: PASS | PASS_WITH_LIMITATIONS | BLOCKED | FAIL
```

---

## 3. 4 Doğrulama Derinliği ve Uygulama Senaryoları

İşinizin getirdiği riske göre sistem 4 farklı derinlik kademesinden birini seçer:

### 1. MINIMAL Derinlik
* **Ne Zaman Seçilir?** Deterministik metin işleme, şablon doldurma, JSON biçimlendirme, regex dönüşümleri, liste filtrelemeleri.
* **Ne Yapar?** Çıktının biçimini, kullanıcı kısıtlarını ve şema kurallarını inceler. Ağır adversarial analiz yapmaz.
* **Örnek Senaryo:** 500 satırlık müşteri listesinden sadece "aktif" ve "Türkiye" olanları JSON olarak çıkarmak.

### 2. STANDARD Derinlik
* **Ne Zaman Seçilir?** Genel kod yazımı, API istemcileri, teknik araştırmalar, kavramsal açıklamalar, planlama.
* **Ne Yapar?** İddiaları ayıklar, her iddia için kanıt arar, mantıksal tutarlılığı ve hafif hasmane senaryoları inceler.
* **Örnek Senaryo:** Python ile async Redis queue kuyruğu tüketicisi yazmak.

### 3. ADVERSARIAL Derinlik
* **Ne Zaman Seçilir?** Mimari tercihler, karmaşık algoritmalar, eşzamanlılık (concurrency/multithreading), güvenlik sınırları, çoklu veri modeli entegrasyonları.
* **Ne Yapar?** Çıktıyı çürütmeye odaklanır. Matematiksel/mantıksal karşıt örnekler (`counterexamples`) arar, gizli varsayımları (`assumptions`) deşifre eder, karşılaştırmalarda taraflılık denetimi yapar.
* **Örnek Senaryo:** İki mikroservis arasındaki dağıtık işlem (saga pattern) tasarımının tutarlılık analizi.

### 4. CRITICAL Derinlik
* **Ne Zaman Seçilir?** Canlı veritabanı migration scriptleri, ödeme ve finansal hesaplama motorları, yetkilendirme/kriptografi mekanizmaları, sıfır-kesinti üretim dağıtım adımları.
* **Ne Yapar?** Dış gerçeklik denetimi zorunludur (derleyici, linter, runtime test veya resmi dokümantasyon kanıtı). Zihinsel mutasyon testi (`mutation testing`) işletilir.
* **Örnek Senaryo:** 10 milyon satırlık PostgreSQL tablosunda tablo kilitlenmesi (table lock) yaratmadan sütun tipi değiştirme.

---

## 4. 18 Doğrulama Deseni: Pratik Örnekler ve Promptlar

Ajanınızın kullanabileceği 18 desen ve bunların pratik uygulamaları:

### Desen 1: Kısıt Doğrulaması (Constraint Verification)
* **Amaç:** Kullanıcının açıkça belirttiği limitleri, formatı ve yasakları doğrulamak.
* **Örnek Prompt:** *"Bana son 5 yılın JavaScript framework'lerini karşılaştır. Kesinlikle React ve Vue'dan bahsetme, en fazla 3 alternatif listele."*
* **Denetim:** Çıktıda React/Vue kelimesi geçti mi? Liste sayısı tam 3 mü? Yıllar 2021 ve sonrası mı?

### Desen 2: Bütünlük / Kapsam Doğrulaması (Completeness Verification)
* **Amaç:** Talep edilen tüm boyutların atlanmadan ele alındığından emin olmak.
* **Kural:** *Uzun cevap, eksiksiz cevap demek değildir.*
* **Örnek Prompt:** *"Yeni API mimarimizi performans, bellek, güvenlik, maliyet ve ölçeklenebilirlik açısından incele."*
* **Denetim:** 5 boyuttan herhangi biri eksik bırakıldıysa `OF-02 (MISSING_CLAIM)` hatası üretilir.

### Desen 3: İddia-Kanıt Eşleştirmesi (Claim-Evidence Verification)
* **Amaç:** İddia edilen teknik verinin doğrudan bir kaynağa dayanmasını sağlamak.
* **Örnek Prompt:** *"Go'daki `sync.Pool` yapısının bellek yönetiminde GC yükünü nasıl azalttığını resmi referanslarla açıkla."*
* **Denetim:** Kaynak gerçekten Go bellek yöneticisinin davranışını kanıtlıyor mu, yoksa model sadece spekülasyon mu yapıyor?

### Desen 4: Varsayım Denetimi (Assumption Audit)
* **Amaç:** Çıktının dayandığı görünmez varsayımları açığa çıkarmak.
* **Örnek:** *"Bu kod O(1) bellek tüketir."* → *Varsayım: Girdi dizisi bellekte zaten mevcuttur ve stream değildir.*
* **Denetim:** Eğer varsayım `UNVERIFIED` ise iddia en fazla `SUPPORTED` olarak etiketlenebilir, `VERIFIED` olamaz (`INV-040`).

### Desen 5: Karşıt Örnek Arama (Counterexample Search)
* **Amaç:** Bir iddiayı çürütmek için somut bir girdi üretmek.
* **Örnek İddia:** *"Bu fonksiyon tüm stringleri geçerli e-postaya dönüştürür veya reddeder."*
* **Karşıt Örnek Testi:** `"user..name@domain.com"`, `".username@domain.com"`, `"trailing@dot."` gibi RFC uç durumları denenir.

### Desen 6: Mantıksal Gerektirme (Logical Entailment)
* **Amaç:** Öncüllerden varılan sonucun mantıksal bir sıçrama (non-sequitur) içermediğini denetlemek.

### Desen 7: Tutarlılık Doğrulaması (Consistency Verification)
* **Amaç:** Metnin veya kodun farklı bölümleri arasındaki çelişkileri yakalamak.
* **Örnek Çelişki:** Giriş bölümünde *"Redis tek iş parçacıklıdır"* deyip, sonuçta *"Redis multithreaded olarak tüm CPU'ları tüketir"* demek (`OF-04`).

### Desen 8: Karşılaştırma Simetrisi (Comparison Symmetry)
* **Amaç:** İki teknolojiyi kıyaslarken birine karşı haksız avantaj/dezavantaj yaratılmasını önlemek.
* **Örnek:** Postgres vs MongoDB kıyaslamasında Postgres'in en yeni sürüm özelliklerini MongoDB'nin 5 yıl önceki sürümüyle kıyaslamak simetriyi bozar.

### Desen 9: Filtreleme Doğrulaması (Filtering Verification)
* **Amaç:** Hem Yanlış Pozitifleri (`OF-06`) hem de Yanlış Negatifleri (`OF-07`) test etmek.
* **Örnek:** *"Sadece Fortune 500'deki yapay zeka şirketlerini getir."* (Alakasız şirket eklendi mi? Girmesi gereken dev şirket unutuldu mu?)

### Desen 10: Sınıflandırma Doğrulaması (Classification Verification)
* **Amaç:** Sınırda kalan (borderline) durumların doğru kategorize edildiğinden emin olmak.

### Desen 11: Dönüşümün Korunumu (Transformation Preservation)
* **Amaç:** Refactoring veya dil çevirisinde anlamsal özelliklerin (semantic invariants) bozulmadığını garantilemek.
* **Örnek:** Python'dan Rust'a taşınan bir fonksiyonda float hassasiyeti ve integer overflow davranışı korundu mu?

### Desen 12: Araştırma Kapsamı (Research Coverage)
* **Amaç:** Endüstri standardı haline gelmiş kütüphane veya yaklaşımların görmezden gelinmediğini denetlemek.

### Desen 13: Öneri Doğrulaması (Recommendation Verification)
* **Amaç:** Bir araç veya mimari önerilirken operasyonel yükünün, maliyetinin ve zayıf yönlerinin gizlenmesini engellemek.

### Desen 14: Dış Gerçeklik Kontrolü (External Reality Check)
* **Amaç:** Modelin kendi zihinsel inancı yerine derleyicileri, linter'ları, curl çağrılarını veya test koşucularını kullanması.

### Desen 15: Mutasyon Testi (Mutation Testing)
* **Amaç:** Test paketinin duyarlılığını ölçmek.
* **Yöntem:** Yanıta kasten bir bug enjekte edilir. Eğer mevcut testler bu hatayı yakalayamazsa testler zayıftır (`VF-02`).

### Desen 16: Doğrulamanın Doğrulanması (Verification-of-Verification)
* **Amaç:** Testlerin döngüsel mantık (`circular reasoning`) içerip içermediğini denetlemek.

### Desen 17: Kanıt Sınırı (Evidence Boundary)
* **Amaç:** Test edilmeyen alanları açıkça `NOT CHECKED` listesine koyup raporlamak.

### Desen 18: Minimal Doğrulama Prensibi (Minimal Verification Principle)
* **Amaç:** Basit sohbetler, selamlaşmalar veya risksiz metin biçimlendirmeleri için gereksiz ağır doğrulama çalıştırmamak.

---

## 5. 4 Karar Durumu ve Örnek Çıktılar

Bir doğrulama oturumu her zaman aşağıdaki 4 durumdan biriyle biter:

### 1. `PASS` (Tam Doğrulandı)
Tüm kritik gereksinimler kanıtlanmış, hiçbir açık hata veya şüphe kalmamıştır.
```markdown
### Doğrulanmış Çözüm
[Kod veya analiz metni temiz şekilde sunulur]

> **Doğrulama Özeti:**
> - Seviye: STANDARD
> - Karar: PASS
> - Belirleyici Kanıt: [EV-001 (Resmi dokümantasyon RFC-7519)]
```

### 2. `PASS_WITH_LIMITATIONS` (Sınırlı Kabul)
Çözüm çalışır durumdadır ancak belirli sınır şartları veya varsayımlar mevcuttur.
```markdown
### Doğrulanmış Çözüm
[Fonksiyon kodu]

> **Kullanım Kısıtları (Disclosed Limitations):**
> - Fonksiyon yalnızca `n <= 100.000` veri boyutu için doğrulanmıştır (CL-003).
> - Bellek kısıtlı IoT cihazlarında stream buffer kullanılmalıdır (INV-047).
```

### 3. `BLOCKED` (Erişim veya Araç Engeli)
Gereken canlı veritabanı veya derleyici ortamı mevcut olmadığı için agent spekülasyon yapmayı reddeder (`INV-010`).
```markdown
> **Doğrulama Durumu: BLOCKED**
> - **Kontrol Edilen:** SQL syntax doğrulaması tamamlandı.
> - **Engellenen:** Canlı Postgres 16 üzerinde EXPLAIN ANALYZE çalıştırılamadı (XF-01).
> - **Gereken Kanıt:** Canlı tablo istatistikleri ve execution planı.
```

### 4. `FAIL` (Doğrulama Başarısız)
Çözüm kısıtları ihlal etmiştir veya 2 revizyon hakkı dolmasına rağmen düzeltilememiştir.
```markdown
> **Doğrulama Durumu: FAIL**
> - **İhlal Edilen Kural:** AC-002 (O(1) yardımcı bellek gereksinimi).
> - **Hata Sınıfı:** OF-10 (Constraint Violation).
> - **Sebep:** Algoritma özyineleme (recursion) sırasında çağrı yığını (call stack) nedeniyle O(log n) bellek kullanmaktadır.
```

---

## 6. Hata Sınıflandırma ve 2-Adımlı Revizyon Kuralı

Bir test başarısız olduğunda sistem panik yapmaz veya ezbere yanıt üretmez:

1. **Sınıflandır:** Hata [`failure-taxonomy.md`](references/failure-taxonomy.md) tablosundaki 29 koddan birine bağlanır (Örn: `OF-04 Contradiction`).
2. **Hedefe Yönelik Revize Et:** Sadece hataya sebep olan iddia düzeltilir.
3. **Eski Testleri Geçersiz Kıl (`INV-003 / INV-048`):** *"Eski testler geçmişti"* denilemez, revize edilen iddia yeniden test edilir.
4. **Tükenme Sınırı (`INV-033`):** Aynı kritik iddia üzerinde **arka arkaya 2 kez başarısız re-test** yaşanırsa revizyon durdurulur ve doğrudan `FAIL` verilir. Sonsuz döngü engellenir.

---

## 7. Farklı Roller İçin Prompt Şablonları

### Yazılım Geliştiriciler İçin
> *"Python'da yüksek trafikli bir rate-limiter sınıfı yaz (Token Bucket algoritması). agent-verification skill'ini CRITICAL seviyede devreye al; eşzamanlılık (race conditions) ve thread-safety için hasmane testler çalıştır."*

### Sistem Mimarları İçin
> *"Mevcut monolit mimarimizi event-driven yapıya geçirmek istiyoruz. Bir geçiş planı hazırla. Planı agent-verification ADVERSARIAL derinlikte test et; veri kaybı ve ağ bölünmesi (network partition) durumlarını karşıt örneklerle sına."*

### Veri Mühendisleri İçin
> *"ClickHouse ile PostgreSQL arasında CDC (Change Data Capture) veri boru hattı tasarla. Tasarımı agent-verification STANDARD derinlikte doğrula; schema drift ve veri tipi uyumsuzluğu risklerini ortaya koy."*

### DevOps / SRE Mühendisleri İçin
> *"Kubernetes üzerinde çalışan stateful bir servis için Blue/Green deployment stratejisi yaz. agent-verification ile depolama birimi (PVC) çakışması ve DNS yayılma gecikmelerini denetle."*

---

## 8. Araç Entegrasyonları

* **Claude Code:** Proje dizininde `npx skills add metodoloji/agent-verification` yaptıktan sonra Claude doğrudan skill'i tanır.
* **Cursor / Windsurf:** Prompt başına `[Agent Verification Protocol: ADVERSARIAL]` ekleyerek modelin doğrulama sözleşmesi kurmasını sağlayabilirsiniz.
* **OpenHands:** `.metodoloji/skills/agent-verification` yoluna semlink vererek agent döngüsüne mechanical gate olarak bağlayabilirsiniz.
