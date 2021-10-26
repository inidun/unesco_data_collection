from courier.elements import AssignPageService, ConsolidateTextService, CourierIssue, IssueStatistics


def test_issue_statistics_has_expected_values():
    issue = CourierIssue('012656')
    assert IssueStatistics(issue).total_pages == 36
    assert IssueStatistics(issue).assigned_pages == 0
    assert IssueStatistics(issue).consolidated_pages == 0
    assert IssueStatistics(issue).expected_article_pages == 24
    assert IssueStatistics(issue).number_of_articles == 5
    assert IssueStatistics(issue).year == 1966
    assert all(missing == 0 for _, _, missing in IssueStatistics(issue).missing_pages)
    assert IssueStatistics(issue).num_missing_pages == 0
    assert IssueStatistics(issue).errors == []
    assert IssueStatistics(issue).num_errors == 0


def test_IssueStatistics_errors_returns_expected_values():
    issue_number = '063436'
    issue = CourierIssue(issue_number)

    AssignPageService().assign(issue)
    ConsolidateTextService().consolidate(issue)

    assert IssueStatistics(issue).assigned_pages == 58
    assert len(IssueStatistics(issue).errors) == 4
