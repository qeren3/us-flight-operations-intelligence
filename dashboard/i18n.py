"""Centralized English / Turkish localization for the Flight Operations Intelligence dashboard."""

from __future__ import annotations

from typing import Any

import streamlit as st

SUPPORTED_LANGUAGES: tuple[str, ...] = ("en", "tr")
DEFAULT_LANGUAGE: str = "en"
LANG_STATE_KEY: str = "dashboard_lang"

MONTHS_SHORT: dict[str, dict[int, str]] = {
    "en": {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
    },
    "tr": {
        1: "Oca", 2: "Şub", 3: "Mar", 4: "Nis", 5: "May", 6: "Haz",
        7: "Tem", 8: "Ağu", 9: "Eyl", 10: "Eki", 11: "Kas", 12: "Ara",
    },
}

MONTHS_FULL: dict[str, dict[int, str]] = {
    "en": {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
    },
    "tr": {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
        7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
    },
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Global chrome & branding
        "app.page_title": "Flight Operations Intelligence",
        "brand.name": "FLIGHT OPERATIONS INTELLIGENCE",
        "brand.subtitle": "2015 US Aviation Operations · Validated Analytics Platform",
        "brand.badge": "2015 DATASET",
        "nav.section": "Navigation",
        "lang.label": "Language",
        "lang.tr_help": "Switch interface language to Turkish",
        "lang.en_help": "Switch interface language to English",

        # Page titles (navigation & headings)
        "page.executive.title": "Executive Overview",
        "page.executive.kicker": "EXECUTIVE INTELLIGENCE",
        "page.executive.desc": "Network-wide flight volume, schedule punctuality, and carrier reliability across the selected 2015 scope.",
        "page.operations.title": "Flight Operations",
        "page.operations.kicker": "OPERATIONAL CADENCE",
        "page.operations.desc": "Monthly throughput, source day-of-week distribution, hourly departure patterns, and disruption rates.",
        "page.airports.title": "Airport Intelligence",
        "page.airports.kicker": "AIRPORT PERFORMANCE",
        "page.airports.desc": "Normalized origin and destination volumes, airport delay rankings, and seasonal departure-delay intensity.",
        "page.routes.title": "Route Intelligence",
        "page.routes.kicker": "CORRIDOR ANALYTICS",
        "page.routes.desc": "High-volume domestic corridors, route-level delay tradeoffs, and monthly trajectory trends using normalized IATA endpoints.",
        "page.delays.title": "Delay Analysis",
        "page.delays.kicker": "ROOT-CAUSE DIAGNOSTICS",
        "page.delays.desc": "Attribution of positive departure delays across operational causes, carrier delay comparisons, and delay distributions.",
        "page.quality.title": "Data Quality",
        "page.quality.kicker": "DATA TRUST & RECONCILIATION",
        "page.quality.desc": "Live PostgreSQL reconciliation checks side by side with the validated Sprint 5 October airport crosswalk audit.",

        # Sidebar filters
        "filter.heading": "Analysis Filters",
        "filter.period_group": "Time & Carrier Scope",
        "filter.page_group": "Page-Specific Focus",
        "filter.months": "Months in 2015",
        "filter.months_help": "Select one or more months in 2015. Clearing all months returns an empty result set.",
        "filter.airlines": "Airlines",
        "filter.airlines_help": "Select carriers to include in the filtered analytical views.",
        "filter.airport_focus": "Airport Focus",
        "filter.airport_focus_help": "Filters origin and destination metrics, rankings, and the monthly heatmap. Leave blank for network-wide totals and top ten origins.",
        "filter.origin": "Origin Airport",
        "filter.origin_help": "Restrict route metrics and monthly trends to a single departure airport.",
        "filter.destination": "Destination Airport",
        "filter.destination_help": "Restrict route metrics and monthly trends to a single arrival airport.",
        "filter.any_origin": "All Origins",
        "filter.any_destination": "All Destinations",
        "filter.reset": "Reset Filters",
        "filter.reset_help": "Restore all 12 months, all 14 airlines, and clear airport/route focus.",
        "filter.placeholder": "Choose options",
        "filter.footnote": "2015 US flight dataset · Cached from local PostgreSQL (5-min TTL).",
        "filter.quality_note": "Data Quality runs fixed validation checks against the complete 2015 cohort and does not use analytical filters.",

        # Active scope summary pills
        "scope.months_all": "All 12 months (2015)",
        "scope.months_count": "{count} of 12 months",
        "scope.months_none": "No months selected",
        "scope.airlines_all": "All {count} airlines",
        "scope.airlines_count": "{count} of {total} airlines",
        "scope.airlines_none": "No airlines selected",
        "scope.airports_focus": "{count} focused airport(s)",
        "scope.route_scope": "Corridor: {scope}",

        # Status, loading, errors, empty states
        "status.loading": "Querying PostgreSQL…",
        "status.empty": "No records match the current filter selection. Adjust the sidebar filters or click Reset Filters.",
        "status.empty_threshold": "No origin airport meets the original 50,000-flight eligibility threshold under these filters.",
        "status.empty_causes": "No positive-departure-delay cause totals are available for this selection.",
        "error.data_unavailable": "Dashboard data is unavailable. Check that local PostgreSQL is running and the project configuration is valid.",
        "error.db_config_hint": "The dashboard connects read-only using the project's local PostgreSQL configuration.",
        "error.cache_hint": "Cached query data expires after five minutes. If the issue persists, check local PostgreSQL availability.",

        # Common units & hover labels
        "unit.flights": "flights",
        "unit.min": "min",
        "unit.hours": "hours",
        "unit.codes": "codes",
        "unit.obs": "observations",
        "label.month": "Month",
        "label.flights": "Flights",
        "label.departures": "Departures",
        "label.arrivals": "Arrivals",
        "label.airport": "Airport",
        "label.airline": "Airline",
        "label.route": "Route",
        "label.origin": "Origin",
        "label.destination": "Destination",
        "label.delay_type": "Delay Type",
        "label.departure": "Departure",
        "label.arrival": "Arrival",
        "label.avg_delay": "Average Delay",
        "label.avg_dep_delay": "Avg Departure Delay",
        "label.avg_arr_delay": "Avg Arrival Delay",
        "label.dep_obs": "Departure Observations",
        "label.arr_obs": "Arrival Observations",
        "label.observed_delays": "Observed Delays",
        "label.cancellation_rate": "Cancellation Rate",
        "label.diversion_rate": "Diversion Rate",
        "label.cancelled_flights": "Cancelled Flights",
        "label.diverted_flights": "Diverted Flights",
        "label.rate": "Rate",
        "label.rate_pct": "Share of Flights (%)",
        "label.cause": "Delay Cause",
        "label.delay_hours": "Total Delay (hours)",
        "label.share": "Share",
        "label.delay_range": "Delay Range",
        "label.scheduled_hour": "Scheduled Departure Hour",
        "label.day_of_week_code": "Source Day-of-Week Code",
        "label.endpoint": "Endpoint",
        "label.metric": "Delay Metric",
        "label.city": "City",

        # Executive Overview
        "exec.kpi.total_flights": "Total Flights",
        "exec.kpi.total_flights_note": "Selected months & carriers",
        "exec.kpi.avg_dep_delay": "Avg Departure Delay",
        "exec.kpi.avg_arr_delay": "Avg Arrival Delay",
        "exec.kpi.obs_note": "{count} observed delays",
        "exec.kpi.cancel_rate": "Cancellation Rate",
        "exec.kpi.cancel_note": "{count} cancelled / all flights",
        "exec.kpi.divert_rate": "Diversion Rate",
        "exec.kpi.divert_note": "{count} diverted / all flights",
        "exec.insight.peak": "{month} recorded the highest flight volume in the active selection with {count} flights ({dep} min avg departure delay).",
        "exec.sec.monthly_vol": "Monthly Flight Volume",
        "exec.sec.monthly_vol_sub": "Total scheduled flights per month in the selected 2015 scope.",
        "exec.sec.monthly_delay": "Monthly Delay Trends",
        "exec.sec.monthly_delay_sub": "Average departure and arrival delay in minutes across months.",
        "exec.sec.airline_perf": "Airline Performance Matrix",
        "exec.sec.airline_perf_sub": "Operating volume versus average departure delay; bubble size reflects flight count and color encodes cancellation rate.",
        "exec.sec.airline_caption": "Airline delay averages use non-NULL delay observations. Cancellation rate uses all flights for each airline as its denominator.",

        # Flight Operations
        "ops.sec.monthly_vol": "Monthly Operating Volume",
        "ops.sec.monthly_vol_sub": "Monthly flight volume across the active selection.",
        "ops.sec.weekday": "Day-of-Week Code Volume",
        "ops.sec.weekday_sub": "Flight counts by numeric source day_of_week code.",
        "ops.sec.weekday_cap": "The dataset stores day_of_week as a numeric source code (1–7); codes are preserved directly without assuming a calendar label mapping.",
        "ops.sec.hourly": "Hourly Departure Delay",
        "ops.sec.hourly_sub": "Average delay across scheduled departure hours (00–23).",
        "ops.sec.hourly_cap": "Hourly KPI: AVG(departure_delay) for rows with non-NULL scheduled_departure in hour buckets 0–23; NULL delays are ignored by SQL AVG.",
        "ops.sec.disruptions": "Cancellation & Diversion Rates",
        "ops.sec.disruptions_sub": "Monthly share of flights cancelled or diverted.",
        "ops.sec.disruptions_cap": "Both rates use all flights in the month and selected airline set as the denominator.",
        "ops.sec.airline_vol": "Carrier Operating Volume",
        "ops.sec.airline_vol_sub": "Top carriers ranked by total flights operated.",
        "ops.hover.hour_fmt": "{hour:02d}:00 – {hour:02d}:59",
        "ops.legend.cancellation": "Cancellation Rate",
        "ops.legend.diversion": "Diversion Rate",

        # Airport Intelligence
        "air.focus_caption": "Airport focus is active on origin/destination metrics, rankings, and the monthly heatmap ({count} selected).",
        "air.sec.top_origin": "Top Origin Airports",
        "air.sec.top_origin_sub": "Highest-volume departure hubs by normalized IATA code.",
        "air.sec.top_dest": "Top Destination Airports",
        "air.sec.top_dest_sub": "Highest-volume arrival hubs by normalized IATA code.",
        "air.sec.rankings": "Airport Delay Rankings",
        "air.sec.rankings_sub": "Compare average departure delay (major hubs) and average arrival delay across endpoints.",
        "air.sec.rank_dep": "Departure Delay · >50,000-Flight Eligibility Threshold",
        "air.sec.rank_arr": "Arrival Delay · Ranked by Average Delay",
        "air.sec.rank_arr_cap": "Arrival ranking is supplemental; the validated Sprint 6 volume threshold (>50,000 flights) applies to origin departures only.",
        "air.sec.heatmap": "Monthly Departure-Delay Heatmap",
        "air.sec.heatmap_sub_focus": "Average departure delay by month for {count} focused origin airport(s).",
        "air.sec.heatmap_sub_default": "Average departure delay by month across the ten busiest origin airports under the active filters.",
        "air.sec.heatmap_cap": "Heatmap averages use non-NULL departure_delay observations without excluding cancelled or diverted flights (Sprint 7 validated KPI).",
        "air.colorbar.title": "Avg Delay<br>(min)",
        "air.table.expander": "Airport Summary Table (Origin & Destination)",
        "air.table.metric_dep": "Departure Delay",
        "air.table.metric_arr": "Arrival Delay",

        # Route Intelligence
        "route.scope_banner": "Active corridor filter: {scope}",
        "route.sec.top_routes": "Top Corridors by Volume",
        "route.sec.top_routes_sub": "Busiest domestic origin-to-destination pairs (top 15 shown).",
        "route.sec.delay_scatter": "Route Delay Profile",
        "route.sec.delay_scatter_sub": "Average departure delay versus average arrival delay across top 30 routes; bubble size reflects volume.",
        "route.sec.monthly_trends": "Monthly Corridor Volume Trends",
        "route.sec.monthly_trends_sub": "Monthly flight volume for the ten highest-volume matching routes.",
        "route.sec.monthly_trends_cap": "Endpoint selectors narrow the route population before the top ten routes are chosen.",
        "route.sec.table": "Route Performance Metrics",
        "route.sec.table_sub": "Top 30 matching routes with volume and delay observation counts.",
        "route.sec.table_cap": "Flight volume counts every matching flight. Average delays use non-NULL observations, matching the Sprint 6 normalized route metrics.",

        # Delay Analysis
        "delay.cause.late_aircraft": "Late Aircraft",
        "delay.cause.airline": "Airline Operations",
        "delay.cause.nas": "Air System (NAS)",
        "delay.cause.weather": "Weather",
        "delay.cause.security": "Security",
        "delay.sec.breakdown": "Delay Root-Cause Breakdown",
        "delay.sec.breakdown_sub": "Total attributed delay hours across the five FAA cause categories (departure_delay > 0).",
        "delay.sec.breakdown_cap": "Preserved root-cause SQL: SUM(cause_delay) / 60 rounded to whole hours over rows where departure_delay > 0. SQL SUM ignores NULL cause values. Shares use the sum of the five displayed cause totals as denominator.",
        "delay.summary.heading": "Cause Attribution Summary",
        "delay.summary.total": "Total Attributed Delay",
        "delay.summary.donut_label": "Total Delay",
        "delay.sec.monthly_causes": "Monthly Delay Cause Trends",
        "delay.sec.monthly_causes_sub": "Stacked monthly delay hours by operational cause.",
        "delay.sec.monthly_causes_cap": "Uses the same departure_delay > 0 condition and SUM/60 hours definition grouped by month.",
        "delay.sec.airline_comp": "Carrier Delay Comparison",
        "delay.sec.airline_comp_sub": "Average departure and arrival delay for the 12 highest-ranked carriers by departure delay.",
        "delay.sec.airline_comp_cap": "Airline averages use non-NULL delay observations across the active filter scope.",
        "delay.sec.distributions": "Delay Distributions",
        "delay.sec.distributions_sub": "Flight counts across 30-minute delay intervals from −60 to 240+ minutes.",
        "delay.sec.dist_dep": "Departure Delay Distribution",
        "delay.sec.dist_arr": "Arrival Delay Distribution",
        "delay.sec.dist_cap": "Distributions include every non-NULL delay value in the selected scope without filtering cancelled or diverted status. Underflow (< −60 min) and overflow (240+ min) are separate bins.",
        "delay.bin.underflow": "< −60 min",
        "delay.bin.overflow": "240+ min",
        "delay.bin.range": "{low} to {high} min",

        # Data Quality
        "dq.sec.historical": "Historical Sprint 5 Audit Baseline",
        "dq.sec.historical_sub": "Validated reference benchmarks recorded during Sprint 5 October airport reconciliation.",
        "dq.sec.historical_cap": "Values above reflect the documented Sprint 5 audit baseline; live metrics below are queried directly from PostgreSQL (5-minute cache).",
        "dq.kpi.hist_flights": "Validated Flight Rows",
        "dq.kpi.hist_flights_note": "Sprint 5 audited total",
        "dq.kpi.hist_oct": "October 2015 Cohort",
        "dq.kpi.hist_oct_note": "Sprint 5 audited rows",
        "dq.kpi.hist_crosswalk": "Crosswalk Mappings",
        "dq.kpi.hist_crosswalk_note": "Official DOT ID → IATA",
        "dq.kpi.hist_validation": "Crosswalk Audit",
        "dq.kpi.hist_validation_val": "20 / 20 PASS",
        "dq.kpi.hist_validation_note": "Sprint 5 read-only checks",
        "dq.sec.live": "Live PostgreSQL Reconciliation",
        "dq.sec.live_sub": "Real-time read-only verification of public.flights_normalized and public.airport_id_iata_crosswalk.",
        "dq.kpi.live_flights": "Live Flight Rows",
        "dq.kpi.live_oct": "Live October Rows",
        "dq.kpi.live_oct_note": "2015-10 cohort",
        "dq.kpi.live_crosswalk": "Live Crosswalk Rows",
        "dq.kpi.live_crosswalk_note": "Source month 2015-10-01",
        "dq.kpi.live_unresolved": "Unresolved Oct Endpoints",
        "dq.kpi.live_unresolved_note": "Origin {orig} · Destination {dest}",
        "dq.kpi.origin_cov": "October Origin Coverage",
        "dq.kpi.dest_cov": "October Destination Coverage",
        "dq.kpi.cov_note": "{pct}% of live October flights",
        "dq.kpi.ref_integrity": "Crosswalk Reference Integrity",
        "dq.kpi.ref_integrity_note": "{missing} missing in airport reference",
        "dq.status.pass_title": "Live Reconciliation Checks: PASS",
        "dq.status.pass_body": "Expected row counts (5,819,079 total; 486,165 October) and crosswalk cardinality (307 distinct IDs & sequences) match the validated Sprint 5 baseline. All October origin and destination endpoints resolve cleanly to the local airport reference.",
        "dq.status.fail_title": "Live Reconciliation Checks: Review Required",
        "dq.status.fail_body": "One or more row-count, crosswalk cardinality, endpoint-coverage, or unresolved-code checks differ from the validated Sprint 5 baseline.",
        "dq.sec.reconciled": "Reconciliation Methodology",
        "dq.sec.reconciled_body": (
            "In October 2015, the source flight feed recorded airport identifiers as numeric DOT Airport IDs while the "
            "project's airport reference table uses 3-letter IATA codes. Sprint 4–5 validated an official 307-row October "
            "crosswalk and exposed normalized origin and destination IATA fields via `public.flights_normalized`. "
            "The crosswalk applies strictly to October 2015; raw identifiers and mapping status remain preserved alongside normalized codes."
        ),
        "dq.sec.reconciled_cap": "The historical PASS benchmark records the Sprint 5 audit. The live status above is recomputed from PostgreSQL tables and views without re-downloading the external BTS archive.",
    },
    "tr": {
        # Global chrome & branding
        "app.page_title": "Uçuş Operasyonları İstihbaratı",
        "brand.name": "FLIGHT OPERATIONS INTELLIGENCE",
        "brand.subtitle": "2015 ABD Havacılık Operasyonları · Doğrulanmış Analitik Platform",
        "brand.badge": "2015 VERİ SETİ",
        "nav.section": "Gezinti",
        "lang.label": "Dil",
        "lang.tr_help": "Arayüz dilini Türkçe yap",
        "lang.en_help": "Arayüz dilini İngilizce yap",

        # Page titles (navigation & headings)
        "page.executive.title": "Yönetici Özeti",
        "page.executive.kicker": "YÖNETİCİ İSTİHBARATI",
        "page.executive.desc": "Seçili 2015 döneminde ağ genelinde uçuş hacmi, tarife dakiklik performansı ve havayolu güvenilirliği.",
        "page.operations.title": "Uçuş Operasyonları",
        "page.operations.kicker": "OPERASYONEL TEMPO",
        "page.operations.desc": "Aylık uçuş hacmi, kaynak gün kodu dağılımı, saatlik kalkış performansı ile iptal ve yönlendirme oranları.",
        "page.airports.title": "Havalimanı İstihbaratı",
        "page.airports.kicker": "HAVALİMANI PERFORMANSI",
        "page.airports.desc": "Normalize edilmiş kalkış ve varış hacimleri, havalimanı gecikme sıralamaları ve mevsimsel gecikme yoğunluğu.",
        "page.routes.title": "Rota İstihbaratı",
        "page.routes.kicker": "KORİDOR ANALİTİĞİ",
        "page.routes.desc": "Normalize IATA kodlarıyla yüksek hacimli iç hat koridorları, rota gecikme karşılaştırmaları ve aylık eğilimler.",
        "page.delays.title": "Gecikme Analizi",
        "page.delays.kicker": "KÖK NEDEN ANALİZİ",
        "page.delays.desc": "Pozitif kalkış gecikmelerinin operasyonel nedenlere dağılımı, havayolu karşılaştırmaları ve gecikme dağılımları.",
        "page.quality.title": "Veri Kalitesi",
        "page.quality.kicker": "VERİ GÜVENİ VE MUTABAKAT",
        "page.quality.desc": "Canlı PostgreSQL doğrulama kontrolleri ile Sprint 5 Ekim havalimanı eşleştirme denetiminin karşılaştırmalı görünümü.",

        # Sidebar filters
        "filter.heading": "Analiz Filtreleri",
        "filter.period_group": "Dönem ve Havayolu Kapsamı",
        "filter.page_group": "Sayfaya Özel Odak",
        "filter.months": "2015 Ayları",
        "filter.months_help": "2015 yılından bir veya daha fazla ay seçin. Tüm ayların temizlenmesi boş sonuç döndürür.",
        "filter.airlines": "Havayolları",
        "filter.airlines_help": "Filtrelenmiş analizlere dahil edilecek havayollarını seçin.",
        "filter.airport_focus": "Havalimanı Odağı",
        "filter.airport_focus_help": "Kalkış/varış metriklerini, sıralamaları ve aylık ısı haritasını filtreler. Ağ geneli ve en yoğun 10 kalkış için boş bırakın.",
        "filter.origin": "Kalkış Havalimanı",
        "filter.origin_help": "Rota metriklerini ve aylık eğilimleri tek bir kalkış havalimanıyla sınırlar.",
        "filter.destination": "Varış Havalimanı",
        "filter.destination_help": "Rota metriklerini ve aylık eğilimleri tek bir varış havalimanıyla sınırlar.",
        "filter.any_origin": "Tüm Kalkışlar",
        "filter.any_destination": "Tüm Varışlar",
        "filter.reset": "Filtreleri Sıfırla",
        "filter.reset_help": "12 ayı ve 14 havayolunu geri yükler, havalimanı ve rota odağını temizler.",
        "filter.placeholder": "Seçenek seçin",
        "filter.footnote": "2015 ABD uçuş veri seti · Yerel PostgreSQL önbelleği (5 dk TTL).",
        "filter.quality_note": "Veri Kalitesi sayfası tüm 2015 veri seti üzerinde sabit doğrulama kontrolleri çalıştırır; analiz filtrelerinden etkilenmez.",

        # Active scope summary pills
        "scope.months_all": "Tüm 12 ay (2015)",
        "scope.months_count": "12 aydan {count} ay",
        "scope.months_none": "Ay seçilmedi",
        "scope.airlines_all": "Tüm {count} havayolu",
        "scope.airlines_count": "{total} havayolundan {count}",
        "scope.airlines_none": "Havayolu seçilmedi",
        "scope.airports_focus": "{count} odaklı havalimanı",
        "scope.route_scope": "Koridor: {scope}",

        # Status, loading, errors, empty states
        "status.loading": "PostgreSQL sorgulanıyor…",
        "status.empty": "Seçili filtrelere uygun kayıt bulunamadı. Yan paneldeki filtreleri güncelleyin veya Filtreleri Sıfırla düğmesine tıklayın.",
        "status.empty_threshold": "Bu filtreler altında 50,000 uçuş eşik değerini karşılayan kalkış havalimanı bulunmamaktadır.",
        "status.empty_causes": "Bu seçim için pozitif kalkış gecikmesi kaynaklı neden toplamı bulunmamaktadır.",
        "error.data_unavailable": "Pano verilerine ulaşılamıyor. Yerel PostgreSQL servisinin çalıştığını ve proje yapılandırmasının geçerli olduğunu kontrol edin.",
        "error.db_config_hint": "Pano, projenin yerel PostgreSQL yapılandırmasını salt okunur modda kullanır.",
        "error.cache_hint": "Önbelleğe alınan sorgu sonuçları beş dakika sonra yenilenir. Sorun devam ederse yerel PostgreSQL erişimini kontrol edin.",

        # Common units & hover labels
        "unit.flights": "uçuş",
        "unit.min": "dk",
        "unit.hours": "saat",
        "unit.codes": "kod",
        "unit.obs": "gözlem",
        "label.month": "Ay",
        "label.flights": "Uçuş Sayısı",
        "label.departures": "Kalkış Sayısı",
        "label.arrivals": "Varış Sayısı",
        "label.airport": "Havalimanı",
        "label.airline": "Havayolu",
        "label.route": "Rota",
        "label.origin": "Kalkış",
        "label.destination": "Varış",
        "label.delay_type": "Gecikme Türü",
        "label.departure": "Kalkış",
        "label.arrival": "Varış",
        "label.avg_delay": "Ortalama Gecikme",
        "label.avg_dep_delay": "Ort. Kalkış Gecikmesi",
        "label.avg_arr_delay": "Ort. Varış Gecikmesi",
        "label.dep_obs": "Kalkış Gözlemi",
        "label.arr_obs": "Varış Gözlemi",
        "label.observed_delays": "Gözlenen Gecikme",
        "label.cancellation_rate": "İptal Oranı",
        "label.diversion_rate": "Yönlendirme Oranı",
        "label.cancelled_flights": "İptal Edilen Uçuş",
        "label.diverted_flights": "Yönlendirilen Uçuş",
        "label.rate": "Oran",
        "label.rate_pct": "Uçuş Payı (%)",
        "label.cause": "Gecikme Nedeni",
        "label.delay_hours": "Toplam Gecikme (saat)",
        "label.share": "Pay",
        "label.delay_range": "Gecikme Aralığı",
        "label.scheduled_hour": "Planlanan Kalkış Saati",
        "label.day_of_week_code": "Kaynak Haftanın Günü Kodu",
        "label.endpoint": "Uç Nokta",
        "label.metric": "Gecikme Metriği",
        "label.city": "Şehir",

        # Executive Overview
        "exec.kpi.total_flights": "Toplam Uçuş",
        "exec.kpi.total_flights_note": "Seçili aylar ve havayolları",
        "exec.kpi.avg_dep_delay": "Ort. Kalkış Gecikmesi",
        "exec.kpi.avg_arr_delay": "Ort. Varış Gecikmesi",
        "exec.kpi.obs_note": "{count} gözlenen gecikme",
        "exec.kpi.cancel_rate": "İptal Oranı",
        "exec.kpi.cancel_note": "{count} iptal / tüm uçuşlar",
        "exec.kpi.divert_rate": "Yönlendirme Oranı",
        "exec.kpi.divert_note": "{count} yönlendirme / tüm uçuşlar",
        "exec.insight.peak": "Aktif seçimde en yüksek uçuş hacmi {count} uçuş ile {month} ayında gerçekleşti (ort. kalkış gecikmesi: {dep} dk).",
        "exec.sec.monthly_vol": "Aylık Uçuş Hacmi",
        "exec.sec.monthly_vol_sub": "Seçili 2015 kapsamında aylık toplam planlanan uçuş sayısı.",
        "exec.sec.monthly_delay": "Aylık Gecikme Eğilimleri",
        "exec.sec.monthly_delay_sub": "Aylar bazında ortalama kalkış ve varış gecikmesi (dakika).",
        "exec.sec.airline_perf": "Havayolu Performans Matrisi",
        "exec.sec.airline_perf_sub": "Uçuş hacmine karşı ortalama kalkış gecikmesi; kabarcık boyutu uçuş sayısını, renk iptal oranını gösterir.",
        "exec.sec.airline_caption": "Havayolu gecikme ortalamaları NULL olmayan gecikme gözlemleriyle hesaplanır. İptal oranı, ilgili havayolunun tüm uçuşlarına bölünerek bulunur.",

        # Flight Operations
        "ops.sec.monthly_vol": "Aylık Operasyon Hacmi",
        "ops.sec.monthly_vol_sub": "Aktif filtre kapsamında aylık toplam uçuş dağılımı.",
        "ops.sec.weekday": "Gün Kodu Bazlı Hacim",
        "ops.sec.weekday_sub": "Sayısal kaynak day_of_week kodlarına göre uçuş sayıları.",
        "ops.sec.weekday_cap": "Veri setinde day_of_week sayısal kaynak kodu (1–7) olarak tutulur; takvim günü varsayımı yapılmadan kaynak kodları korunur.",
        "ops.sec.hourly": "Saatlik Kalkış Gecikmesi",
        "ops.sec.hourly_sub": "Planlanan kalkış saatlerine (00–23) göre ortalama gecikme.",
        "ops.sec.hourly_cap": "Saatlik KPI: 0–23 saat dilimlerinde scheduled_departure değeri dolu kayıtlar için AVG(departure_delay); SQL AVG, NULL değerleri hariç tutar.",
        "ops.sec.disruptions": "İptal ve Yönlendirme Oranları",
        "ops.sec.disruptions_sub": "İptal edilen veya yönlendirilen uçuşların aylık yüzdelik payı.",
        "ops.sec.disruptions_cap": "Her iki oran da ilgili ay ve seçili havayolu kümesindeki tüm uçuşları payda olarak kullanır.",
        "ops.sec.airline_vol": "Havayolu Operasyon Hacmi",
        "ops.sec.airline_vol_sub": "Toplam uçuş sayısına göre sıralanan havayolları.",
        "ops.hover.hour_fmt": "{hour:02d}:00 – {hour:02d}:59",
        "ops.legend.cancellation": "İptal Oranı",
        "ops.legend.diversion": "Yönlendirme Oranı",

        # Airport Intelligence
        "air.focus_caption": "Havalimanı odağı kalkış/varış metrikleri, sıralamalar ve aylık ısı haritasında etkindir ({count} seçili).",
        "air.sec.top_origin": "En Yoğun Kalkış Havalimanları",
        "air.sec.top_origin_sub": "Normalize IATA koduna göre en yüksek kalkış hacmine sahip merkezler.",
        "air.sec.top_dest": "En Yoğun Varış Havalimanları",
        "air.sec.top_dest_sub": "Normalize IATA koduna göre en yüksek varış hacmine sahip merkezler.",
        "air.sec.rankings": "Havalimanı Gecikme Sıralamaları",
        "air.sec.rankings_sub": "Büyük merkezlerde ortalama kalkış gecikmesi ile varış gecikmesi karşılaştırması.",
        "air.sec.rank_dep": "Kalkış Gecikmesi · 50,000+ Uçuş Uygunluk Eşiği",
        "air.sec.rank_arr": "Varış Gecikmesi · Ortalama Gecikmeye Göre Sıralı",
        "air.sec.rank_arr_cap": "Varış sıralaması tamamlayıcı niteliktedir; doğrulanmış Sprint 6 hacim eşiği (>50,000 uçuş) yalnızca kalkış havalimanlarına uygulanır.",
        "air.sec.heatmap": "Aylık Kalkış Gecikmesi Isı Haritası",
        "air.sec.heatmap_sub_focus": "Seçili {count} kalkış havalimanı için aylık ortalama kalkış gecikmesi.",
        "air.sec.heatmap_sub_default": "Aktif filtreler altında en yoğun 10 kalkış havalimanı için aylık ortalama kalkış gecikmesi.",
        "air.sec.heatmap_cap": "Isı haritası ortalamaları, iptal/yönlendirme filtresi uygulanmadan NULL olmayan departure_delay gözlemlerini kullanır (Sprint 7 doğrulanmış KPI).",
        "air.colorbar.title": "Ort. Gecikme<br>(dk)",
        "air.table.expander": "Havalimanı Özet Tablosu (Kalkış ve Varış)",
        "air.table.metric_dep": "Kalkış Gecikmesi",
        "air.table.metric_arr": "Varış Gecikmesi",

        # Route Intelligence
        "route.scope_banner": "Aktif koridor filtresi: {scope}",
        "route.sec.top_routes": "Hacme Göre En Yoğun Koridorlar",
        "route.sec.top_routes_sub": "En yoğun iç hat kalkış–varış çiftleri (ilk 15 rota).",
        "route.sec.delay_scatter": "Rota Gecikme Profili",
        "route.sec.delay_scatter_sub": "En yoğun 30 rotada ortalama kalkış ve varış gecikmesi ilişkisi; kabarcık boyutu uçuş hacmini gösterir.",
        "route.sec.monthly_trends": "Aylık Koridor Hacim Eğilimleri",
        "route.sec.monthly_trends_sub": "Eşleşen en yoğun 10 rota için aylık uçuş hacmi.",
        "route.sec.monthly_trends_cap": "Kalkış ve varış seçicileri, ilk 10 rota belirlenmeden önce rota havuzunu daraltır.",
        "route.sec.table": "Rota Performans Metrikleri",
        "route.sec.table_sub": "Eşleşen ilk 30 rota için hacim ve gecikme gözlem sayıları.",
        "route.sec.table_cap": "Uçuş hacmi eşleşen tüm uçuşları sayar. Ortalama gecikmeler Sprint 6 normalize rota metrikleriyle uyumlu olarak NULL olmayan gözlemleri kullanır.",

        # Delay Analysis
        "delay.cause.late_aircraft": "Geç Gelen Uçak",
        "delay.cause.airline": "Havayolu Operasyonları",
        "delay.cause.nas": "Hava Trafik Sistemi (NAS)",
        "delay.cause.weather": "Hava Koşulları",
        "delay.cause.security": "Güvenlik",
        "delay.sec.breakdown": "Gecikme Kök Neden Dağılımı",
        "delay.sec.breakdown_sub": "Beş FAA gecikme kategorisinde toplam gecikme saatleri (departure_delay > 0).",
        "delay.sec.breakdown_cap": "Korunan kök neden SQL tanımı: departure_delay > 0 olan satırlarda SUM(cause_delay) / 60 tam saate yuvarlanır. SQL SUM, NULL değerleri yok sayar. Yüzdeler gösterilen beş nedenin toplamına göre hesaplanır.",
        "delay.summary.heading": "Neden Bazlı Gecikme Özeti",
        "delay.summary.total": "Toplam Gecikme",
        "delay.summary.donut_label": "Toplam Gecikme",
        "delay.sec.monthly_causes": "Aylık Gecikme Nedeni Eğilimleri",
        "delay.sec.monthly_causes_sub": "Operasyonel nedenlere göre yığılmış aylık gecikme saatleri.",
        "delay.sec.monthly_causes_cap": "Aynı departure_delay > 0 koşulu ve SUM/60 saat tanımı ay bazında gruplanarak uygulanır.",
        "delay.sec.airline_comp": "Havayolu Gecikme Karşılaştırması",
        "delay.sec.airline_comp_sub": "Ortalama kalkış gecikmesine göre ilk 12 havayolu için kalkış ve varış gecikmesi.",
        "delay.sec.airline_comp_cap": "Havayolu ortalamaları, aktif filtre kapsamında NULL olmayan gecikme gözlemleriyle hesaplanır.",
        "delay.sec.distributions": "Gecikme Dağılımları",
        "delay.sec.distributions_sub": "−60 ile 240+ dakika arasında 30 dakikalık aralıklara göre uçuş sayıları.",
        "delay.sec.dist_dep": "Kalkış Gecikmesi Dağılımı",
        "delay.sec.dist_arr": "Varış Gecikmesi Dağılımı",
        "delay.sec.dist_cap": "Dağılımlar, iptal veya yönlendirme filtresi uygulanmadan seçili kapsamdaki tüm NULL olmayan gecikme gözlemlerini içerir. Alt sınır (< −60 dk) ve üst sınır (240+ dk) ayrı aralıklardır.",
        "delay.bin.underflow": "< −60 dk",
        "delay.bin.overflow": "240+ dk",
        "delay.bin.range": "{low} – {high} dk",

        # Data Quality
        "dq.sec.historical": "Sprint 5 Tarihsel Denetim Referansı",
        "dq.sec.historical_sub": "Sprint 5 Ekim havalimanı eşleştirme doğrulaması sırasında kaydedilen referans metrikler.",
        "dq.sec.historical_cap": "Yukarıdaki değerler Sprint 5 denetim kayıtlarıdır; aşağıdaki canlı metrikler PostgreSQL üzerinden doğrudan sorgulanır (5 dk önbellek).",
        "dq.kpi.hist_flights": "Doğrulanan Uçuş Satırı",
        "dq.kpi.hist_flights_note": "Sprint 5 denetim toplamı",
        "dq.kpi.hist_oct": "Ekim 2015 Kohortu",
        "dq.kpi.hist_oct_note": "Sprint 5 denetim satırları",
        "dq.kpi.hist_crosswalk": "Eşleştirme Kaydı",
        "dq.kpi.hist_crosswalk_note": "Resmi DOT ID → IATA",
        "dq.kpi.hist_validation": "Eşleştirme Denetimi",
        "dq.kpi.hist_validation_val": "20 / 20 GEÇTİ",
        "dq.kpi.hist_validation_note": "Sprint 5 salt okunur testler",
        "dq.sec.live": "Canlı PostgreSQL Mutabakatı",
        "dq.sec.live_sub": "public.flights_normalized ve public.airport_id_iata_crosswalk üzerinde gerçek zamanlı salt okunur doğrulama.",
        "dq.kpi.live_flights": "Canlı Uçuş Satırı",
        "dq.kpi.live_oct": "Canlı Ekim Satırı",
        "dq.kpi.live_oct_note": "2015-10 kohortu",
        "dq.kpi.live_crosswalk": "Canlı Eşleştirme Satırı",
        "dq.kpi.live_crosswalk_note": "Kaynak ay 2015-10-01",
        "dq.kpi.live_unresolved": "Çözümlenemeyen Ekim Uçları",
        "dq.kpi.live_unresolved_note": "Kalkış {orig} · Varış {dest}",
        "dq.kpi.origin_cov": "Ekim Kalkış Kapsamı",
        "dq.kpi.dest_cov": "Ekim Varış Kapsamı",
        "dq.kpi.cov_note": "Canlı Ekim uçuşlarının %{pct}'i",
        "dq.kpi.ref_integrity": "Eşleştirme Referans Bütünlüğü",
        "dq.kpi.ref_integrity_note": "Havalimanı referansında {missing} eksik",
        "dq.status.pass_title": "Canlı Mutabakat Kontrolleri: BAŞARILI",
        "dq.status.pass_body": "Beklenen satır sayıları (5,819,079 toplam; 486,165 Ekim) ve eşleştirme kardinalitesi (307 benzersiz ID ve sekans) doğrulanmış Sprint 5 referansıyla birebir eşleşiyor. Tüm Ekim kalkış ve varış uçları yerel havalimanı referansına eksiksiz çözümleniyor.",
        "dq.status.fail_title": "Canlı Mutabakat Kontrolleri: İnceleme Gerekli",
        "dq.status.fail_body": "Satır sayısı, eşleştirme kardinalitesi, uç nokta kapsamı veya çözümlenemeyen kod kontrollerinden biri veya birkaçı doğrulanmış Sprint 5 referansından farklı.",
        "dq.sec.reconciled": "Eşleştirme Metodolojisi",
        "dq.sec.reconciled_body": (
            "Ekim 2015 kaynak uçuş verisinde havalimanı tanımlayıcıları sayısal DOT Airport ID olarak kaydedilirken, "
            "projenin havalimanı referans tablosu 3 harfli IATA kodlarını kullanmaktadır. Sprint 4–5 kapsamında resmi "
            "307 satırlık Ekim eşleştirme tablosu doğrulanmış ve normalize kalkış/varış IATA alanları "
            "`public.flights_normalized` görünümü üzerinden sunulmuştur. Eşleştirme yalnızca Ekim 2015'e uygulanır; "
            "ham kodlar ve eşleştirme durumu görünümde korunmaya devam eder."
        ),
        "dq.sec.reconciled_cap": "Tarihsel başarı kaydı Sprint 5 denetimini yansıtır. Yukarıdaki canlı durum mevcut PostgreSQL tablo ve görünümlerinden yeniden hesaplanır; harici BTS arşivi yeniden indirilmez.",
    },
}


def get_lang() -> str:
    """Return the active UI language ('en' or 'tr'), persisting in session_state."""
    lang = st.session_state.get(LANG_STATE_KEY, DEFAULT_LANGUAGE)
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
        st.session_state[LANG_STATE_KEY] = lang
    return lang


def set_lang(lang: str) -> None:
    """Set the active UI language without touching analytical filters or current page."""
    if lang in SUPPORTED_LANGUAGES and lang != st.session_state.get(LANG_STATE_KEY):
        st.session_state[LANG_STATE_KEY] = lang
        st.session_state["dashboard_lang_gen"] = int(st.session_state.get("dashboard_lang_gen", 0)) + 1


def t(key: str, lang: str | None = None, **kwargs: Any) -> str:
    """Translate a key in the active (or specified) language with English fallback."""
    active = lang if lang in SUPPORTED_LANGUAGES else get_lang()
    template = TRANSLATIONS.get(active, {}).get(key)
    if template is None:
        template = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
    if kwargs:
        return template.format(**kwargs)
    return template


def month_name(month: Any, lang: str | None = None, *, short: bool = True) -> str:
    """Return localized short or full month name for an integer month (1–12)."""
    active = lang if lang in SUPPORTED_LANGUAGES else get_lang()
    table = MONTHS_SHORT if short else MONTHS_FULL
    try:
        return table[active].get(int(month), str(month))
    except (TypeError, ValueError):
        return str(month)


def upper_localized(text: str, lang: str | None = None) -> str:
    """Uppercase text respecting Turkish dotted/dotless I rules."""
    active = lang if lang in SUPPORTED_LANGUAGES else get_lang()
    if active == "tr":
        return text.replace("i", "İ").replace("ı", "I").upper()
    return text.upper()


def delay_bin_label(bin_id: Any, fallback: str = "", lang: str | None = None, *, compact: bool = False) -> str:
    """Format a 30-minute delay histogram bin label in the active language."""
    active = lang if lang in SUPPORTED_LANGUAGES else get_lang()
    try:
        idx = int(bin_id)
    except (TypeError, ValueError):
        return fallback
    if compact:
        if idx == -1:
            return "< −60"
        if idx == 10:
            return "240+"
        return f"{idx * 30 - 60}–{idx * 30 - 30}"
    if idx == -1:
        return t("delay.bin.underflow", active)
    if idx == 10:
        return t("delay.bin.overflow", active)
    return t("delay.bin.range", active, low=idx * 30 - 60, high=idx * 30 - 30)
