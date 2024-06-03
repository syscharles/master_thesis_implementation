from analysis_manager import AnalysisManager
from pipeline_tools.cluster_analysis.cluster_identification import ClusteringAlgorithm

def main():
    '''
    This runs the analysis on the real-world framework Joda-time.
    '''
    data_path = './thesis_code/data/joda_time'
    clustering_algorithm = ClusteringAlgorithm.LOUVAIN
    analysis_manager = AnalysisManager(data_path, clustering_algorithm)
    analysis_manager.run_analysis()
    
if __name__ == '__main__':
    main()