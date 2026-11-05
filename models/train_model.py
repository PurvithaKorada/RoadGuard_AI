from agents.road_risk_agent import RoadRiskAgent

if __name__ == '__main__':
    r = RoadRiskAgent()
    r.load_data()
    report, cm = r.train_model()
    print('Training complete. Classification report:')
    print(report)
    print('Confusion matrix:')
    print(cm)
