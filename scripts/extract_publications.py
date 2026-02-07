#!/usr/bin/env python3
"""
One-off script to extract publications from pages/publications.html
and write configs/publications.yaml. Run from project root.
Requires: pip install beautifulsoup4 pyyaml
"""
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Run: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)
try:
    import yaml
except ImportError:
    print("Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# manualCategories from the existing script (title -> list of category slugs)
MANUAL_CATEGORIES = {
    'NuwaDynamics+: A Causality-Aware Generative Framework for Spatio-Temporal Representation Learning': ['stm'],
    'FaST: Efficient and Effective Long-Horizon Forecasting for Large-Scale Spatial-Temporal Graphs via Mixture-of-Experts': ['time-series', 'graph'],
    'How to Train Your Mamba for Time Series Forecasting': ['time-series'],
    'OccamVTS: Distilling Vision Models to 1% Parameters for Time Series Forecasting': ['time-series', 'multimodal'],
    'Revitalizing Canonical Pre-Alignment for Irregular Multivariate Time Series Forecasting': ['time-series'],
    'A Retrieval Augmented Spatio-Temporal Framework for Traffic Prediction': ['stm'],
    'Damba-ST: Domain-Adaptive Mamba for Efficient Urban Spatio-Temporal Prediction': ['stm'],
    'Bayesian-Driven Graph Reasoning for Active Radio Map Construction': ['graph'],
    'Cross Space and Time: A Spatio-Temporal Unitized Model for Traffic Flow Forecasting': ['stm', 'time-series'],
    'Learning to Factorize Spatio-Temporal Foundation Models': ['stm', 'time-series'],
    'UniTraj: Learning a Universal Trajectory Foundation Model from Billion-Scale Worldwide Traces': ['stm'],
    'FlowNet: Modeling Dynamic Spatio-Temporal Systems via Flow Propagation': ['stm', 'time-series'],
    'Improving Bilinear RNN with Closed-loop Control': ['time-series'],
    'Learning with Calibration: Exploring Test-Time Computing of Spatio-Temporal Forecasting': ['stm', 'time-series'],
    'ShapeX: Shapelet-Driven Post Hoc Explanations for Time Series Classification Models': ['time-series'],
    'Recognition through Reasoning: Reinforcing Image Geo-localization with Large Vision-Language Models': ['multimodal'],
    'Aeolus: A Multi-structural Flight Delay Dataset': ['others'],
    'Not All Data are Good Labels: On the Self-supervised Labeling for Time Series Forecasting': ['time-series'],
    'ST-LoRA: Low-rank Adaptation for Spatio-Temporal Forecasting': ['stm', 'time-series'],
    'Towards Multi-Scenario Forecasting of Building Electricity Loads with Multimodal Data': ['multimodal', 'time-series'],
    'Test-Time Graph Rebirth: Serving GNN Generalization Under Distribution Shifts': ['graph'],
    'Space-aware Socioeconomic Indicator Inference with Heterogeneous Graphs': ['graph'],
    'Fine-grained Urban Heat Island Effect Forecasting: A Context-aware Thermodynamic Modeling Framework': ['stm'],
    'Learning Generalized and Flexible Trajectory Models from Omni-Semantic Supervision': ['stm'],
    'Efficient Large-Scale Traffic Forecasting with Transformers: A Spatial Data Management Perspective': ['stm', 'time-series'],
    'DynST: Dynamic Sparse Training for Resource-Constrained Spatio-Temporal Forecasting': ['stm', 'time-series'],
    'Foundation Models for Spatio-Temporal Data Science: A Tutorial and Survey': ['stm', 'survey', 'time-series'],
    'Moirai-MoE: Empowering Time Series Foundation Models with Sparse Mixture of Experts': ['time-series'],
    'Time-VLM: Exploring Multimodal Vision-Language Models for Augmented Time Series Forecasting': ['time-series', 'multimodal'],
    'Reinforcement learning for hybrid charging stations planning and operation considering fixed and mobile chargers': ['others'],
    'Nature Makes No Leaps: Building Continuous Location Embeddings with Satellite Imagery from the Web': ['multimodal'],
    'Deep Learning for Multivariate Time Series Imputation: A Survey': ['time-series', 'survey'],
    'AdaMove: Efficient Test-Time Adaptation for Human Mobility Prediction': ['stm'],
    'JointDistill: Adaptive Multi-Task Distillation for Joint Depth Estimation and Scene Segmentation': ['multimodal'],
    'Expand and Compress: Exploring TuningPrinciples for Continual Spatio-Temporal GraphForecasting': ['stm', 'graph'],
    'Open-CK: A Large Multi-Physics Fields Coupling benchmarks in Combustion Kinetics': ['others'],
    'Air Quality Prediction with Physics-Informed Dual Neural ODEs in Open Systems': ['stm', 'time-series'],
    'Towards Neural Scaling Laws for Time Series Foundation Models': ['time-series'],
    'AirRadar: Inferring Nationwide Air Quality in China with Deep Neural Networks': ['stm'],
    'UrbanVLP: A Multi-Granularity Vision-Language Pre-Trained Foundation Model for Urban Indicator Prediction': ['multimodal', 'stm'],
    'Unlocking the Power of LSTM for Long Term Time Series Forecasting': ['time-series'],
    'Through the Dual-Prism: A Spectral Perspective on Graph Data Augmentation for Graph Classification': ['graph'],
    'UniTR: A Unified Framework for Joint Representation Learning of Trajectories and Road Networks': ['stm', 'graph'],
    'Personalized Federated Learning for Spatio-Temporal Forecasting: A Dual Semantic Alignment-Based Contrastive Approach': ['stm', 'time-series'],
    'A tensor decomposition method based on embedded geographic meta-knowledge for urban traffic flow imputation': ['stm'],
    'Deep learning for cross-domain data fusion in urban computing: Taxonomy, advances, and outlook': ['multimodal', 'survey'],
    'A Survey on Service Route and Time Prediction in Instant Delivery: Taxonomy, Progress, and Prospects': ['survey', 'stm'],
    'Modeling Spatio-temporal Dynamical Systems with Neural Discrete Learning and Levels-of-Experts': ['stm', 'time-series'],
    'Self-supervised learning for time series analysis: Taxonomy, progress, and prospects': ['time-series', 'survey'],
    'Semantic-fused multi-granularity cross-city traffic prediction': ['stm'],
    'On regularization for explaining graph neural networks: An information theory perspective': ['graph'],
    'Terra: A Multimodal Spatio-Temporal Dataset Spanning the Earth': ['multimodal', 'stm'],
    'Time-FFM: Towards LM-Empowered Federated Foundation Model for Time Series Forcasting': ['time-series'],
    'Attractor memory for long-term time series forecasting: A chaos perspective': ['time-series'],
    'GDeR: Safeguarding Efficiency, Balancing, and Robustness via Prototypical Graph Pruning': ['graph'],
    'Improving Generalization of Dynamic Graph Learning via Environment Prompt': ['graph'],
    'UrbanCross: Enhancing Satellite Image-Text Retrieval with Cross-Domain Adaptation': ['multimodal'],
    'Foundation models for time series analysis: A tutorial and survey': ['time-series', 'survey'],
    'Reinventing Node-Centric Traffic Forecasting for Improved Accuracy and Efficiency': ['stm', 'time-series'],
    'The Heterophily Snowflake Hypothesis: Training and Empowering GNN for Heterophilic Graphs': ['graph'],
    'Spatio-Temporal Graph Neural Networks for Predictive Learning in Urban Computing: A Survey': ['survey', 'stm', 'graph'],
    'AutoSTG+: An Automatic Framework to Discover The Optimal Network for Spatio-temporal Graph Prediction': ['stm', 'graph'],
    'End-to-end Delay Modeling via Leveraging Competitive Interaction among Network Flows': ['others'],
    'LargeST: A Benchmark Dataset for Large-Scale Traffic Forecasting (DB Track)': ['stm', 'time-series'],
    'Maintaining the Status Quo: Capturing Invariant Relations for OOD Spatiotemporal Learning': ['stm'],
    'Contrastive Trajectory Similarity Learning with Dual-Feature Attention': ['stm'],
    'Searching Lottery Tickets in Graph Neural Networks: A Dual Perspective': ['graph'],
    'AirFormer: Predicting Nationwide Air Quality in China with Transformers': ['stm'],
    'PetalView: Fine-grained Location and Orientation Extraction of Street-view Images via Cross-view Local Search': ['multimodal'],
    'DiffSTG: Probabilistic Spatio-Temporal Graph Forecasting with Denoising Diffusion Models': ['stm', 'graph'],
    'Mixed-Order Relation-Aware Recurrent Neural Networks for Spatio-Temporal Forecasting': ['stm', 'time-series'],
    'Beyond Geo-localization: Fine-grained Orientation of Street-view Images by Cross-view Matching with Satellite Imagery': ['multimodal'],
    'When Do Contrastive Learning Signals Help Spatio-Temporal Graph Forecasting?': ['stm', 'graph'],
    'Dualformer: Local-global stratified transformer for efficient video recognition': ['multimodal'],
    'TrajFormer: Efficient Trajectory Classification with Transformers': ['stm'],
    'Periodic Residual Learning for Crowd Flow Forecasting': ['stm'],
    'Time-Aware Neighbor Sampling on Temporal Graphs': ['graph'],
    'Should We Rely on Entity Mentions for Relation Extraction? Debiasing Relation Extraction with Counterfactual Analysis': ['others'],
    'Visual Cascade Analytics of Large-Scale Spatiotemporal Data': ['stm'],
    'Modeling Trajectories with Neural Ordinary Differential Equations': ['stm'],
    'Fine-grained Urban Flow Prediction': ['stm'],
    'AutoSTG: Neural Architecture Search for Predictions of Spatio-Temporal Graph': ['stm', 'graph'],
    'Mixup for Node and Graph Classification': ['graph'],
    'Curgraph: Curriculum learning for graph classification': ['graph'],
    'Directed Graph Contrastive Learning': ['graph'],
    'Adaptive Data Augmentation on Temporal Graphs': ['graph'],
    'Learning Multi-context Aware Location Representations from Large-scale Geotagged Images': ['multimodal'],
    'Fine-grained Urban Flow Inference': ['stm'],
    'Predicting Citywide Crowd Flows in Irregular Regions using Multi-View Graph Convolutional Networks': ['stm', 'graph'],
    'Spatio-Temporal Meta Learning for Urban Traffic Prediction': ['stm'],
    'Predicting Urban Water Quality with Ubiquitous Data – a Data-Driven Approach': ['stm'],
    'Nodeaug: Semi-Supervised Node Classification with Data Augmentation': ['graph'],
    'Digraph Inception Convolutional Networks': ['graph'],
    'Revisiting convolutional neural networks for citywide crowd flow analytics': ['stm'],
    'Autost: Efficient Neural Architecture Search for Spatio-Temporal Prediction': ['stm', 'graph'],
    'Dynamic Public Resource Allocation based on Human Mobility Prediction': ['stm'],
    'Learning to Generate Maps from Trajectories': ['stm'],
    'Progressive Supervision for Node Classification': ['graph'],
    'Unsupervised Learning of Disentangled Location Embeddings': ['stm'],
    'Urban Traffic Prediction from Spatio-Temporal Data using Deep Meta Learning': ['stm'],
    'Urbanfm: Inferring Fine-Grained Urban Flows': ['stm'],
    'Learning Multi-Objective Rewards and User Utility Function in Contextual Bandits for Personalized Ranking': ['others'],
    'GeoMAN: Multi-Level Attention Networks for Geo-sensory Time Series Prediction.': ['stm', 'time-series'],
    'Inferring Traffic Cascading Patterns': ['stm'],
    'Urban Water Quality Prediction based on Multi-Task Multi-View Learning': ['stm'],
    'Federated Forest': ['others']
}

JOURNAL_PATTERN = re.compile(
    r'TPAMI|TITS|TKDE|TNNLS|TOIS|WCSP|TVCG|Journal|IEEE Trans', re.I
)


def norm_title(t):
    if not t:
        return ''
    return re.sub(r'\s+', ' ', re.sub(r'[\u200b-\u200d\ufeff]', '', t)).strip()


def _has_class(tag, name):
    if not tag or not tag.get('class'):
        return False
    c = tag.get('class')
    return name in (c if isinstance(c, list) else [c])


def find_paper_columns(scope):
    """Find column divs that contain both .title and .wp-block-image (paper blocks)."""
    cols = []
    for block in scope.find_all(class_=lambda c: c and ('wp-block-themeisle-blocks-advanced-columns' in (c if isinstance(c, list) else [c]))):
        if not block.find(class_='title') or not block.find(class_='wp-block-image'):
            continue
        nested = block.find(class_=lambda c: c and ('wp-block-themeisle-blocks-advanced-columns' in (c if isinstance(c, list) else [c])))
        if nested and nested.find(class_='title') and nested.find(class_='wp-block-image'):
            continue
        par = block.find_parent(class_=lambda c: c and ('wp-block-themeisle-blocks-advanced-column' in (c if isinstance(c, list) else [c])))
        if par and not par.find_parent(class_='pub-entry'):
            cols.append(par)
    return cols


def get_title(col):
    strong = col.find(class_='title')
    if not strong:
        return ''
    s = strong.find('strong')
    return norm_title(s.get_text()) if s else ''


def get_author(col):
    auth = col.find(class_='author')
    if not auth:
        return ''
    return norm_title(auth.get_text())


def get_venue_and_links(col):
    """Return (venue_text, is_journal, pdf_link, code_link, dataset_link)."""
    venue_text = ''
    is_journal = False
    pdf_link = None
    code_link = None
    dataset_link = None
    for div in col.find_all('div', recursive=True):
        strong = div.find('strong')
        if not strong:
            continue
        text = strong.get_text() or ''
        if JOURNAL_PATTERN.search(text):
            is_journal = True
        if re.match(r'^(20\d{2}|Before 2020|TPAMI|TITS|TKDE|KDD|ICML|NeurIPS|AAAI|WWW|ICDE|IJCAI|MM|SIGSPATIAL|NAACL|IJCNN|WCSP|TVCG|TRC|InfoFusion|ACM MM)', text, re.I) or len(text) < 30:
            venue_text = norm_title(text)
        for a in div.find_all('a', href=True):
            t = norm_title(a.get_text())
            href = a.get('href', '').strip()
            if t == 'PDF':
                pdf_link = href
            elif t == 'CODE':
                code_link = href
            elif t == 'DATASET':
                dataset_link = href
    return (venue_text, is_journal, pdf_link, code_link, dataset_link)


def get_image(col):
    img = col.find('img', src=True)
    return img.get('src', '') if img else ''


def get_year_from_tab(tab_item):
    header = tab_item.find(class_='wp-block-themeisle-blocks-tabs-item__header')
    if not header:
        return ''
    t = norm_title(header.get_text())
    if re.match(r'^202\d$', t):
        return t
    if re.search(r'before\s*2020', t, re.I):
        return 'before2020'
    return t


def main():
    root = Path(__file__).resolve().parent.parent
    html_path = root / 'pages' / 'publications.html'
    yaml_path = root / 'configs' / 'publications.yaml'

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    main_tabs = soup.find(id='wp-block-themeisle-blocks-tabs-ed27d658')
    if not main_tabs:
        print('Main tabs not found', file=sys.stderr)
        sys.exit(1)
    all_tab = main_tabs.find(attrs={'data-pub-filter': 'all'})
    if not all_tab:
        print('All tab not found', file=sys.stderr)
        sys.exit(1)
    all_content = all_tab.find(class_='wp-block-themeisle-blocks-tabs-item__content')
    if not all_content:
        print('All content not found', file=sys.stderr)
        sys.exit(1)
    inner_tabs = all_content.find(class_=lambda c: c and 'wp-block-themeisle-blocks-tabs' in (c if isinstance(c, list) else [c]))
    if not inner_tabs:
        print('Inner tabs not found', file=sys.stderr)
        sys.exit(1)
    inner_content = inner_tabs.find(class_=lambda c: c and 'wp-block-themeisle-blocks-tabs__content' in (c if isinstance(c, list) else [c]))
    year_tab_items = (inner_content or inner_tabs).find_all(class_=lambda c: c and 'wp-block-themeisle-blocks-tabs-item' in (c if isinstance(c, list) else [c]), recursive=False)

    out = []
    seen_titles = set()
    for year_item in year_tab_items:
        year = get_year_from_tab(year_item)
        if not year:
            continue
        content = year_item.find(class_='wp-block-themeisle-blocks-tabs-item__content')
        if not content:
            continue
        for col in find_paper_columns(content):
            title = get_title(col)
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            authors = get_author(col)
            venue_text, is_journal, pdf_link, code_link, dataset_link = get_venue_and_links(col)
            image = get_image(col)
            cats = list(MANUAL_CATEGORIES.get(title, ['others']))
            if not cats:
                cats = ['others']
            entry = {
                'title': title,
                'authors': authors or '',
                'venue': venue_text or '',
                'year': int(year) if year.isdigit() else year,
                'is_journal': is_journal,
                'categories': cats,
                'image': image or '',
                'pdf_link': pdf_link or '',
                'code_link': code_link or '',
                'dataset_link': dataset_link or '',
            }
            out.append(entry)

    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write('# Publications list. Edit this file; page loads it and renders automatically.\n')
        f.write('# Schema: title, authors, venue, year (int or "before2020"), is_journal, categories, image, pdf_link, code_link?, dataset_link?\n\n')
        yaml.dump(out, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=1000)
    print(f'Wrote {len(out)} publications to {yaml_path}')


if __name__ == '__main__':
    main()
