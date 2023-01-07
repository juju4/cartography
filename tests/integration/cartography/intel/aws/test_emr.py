import cartography.intel.aws.emr
import tests.data.aws.emr
from tests.integration.util import check_nodes
from tests.integration.util import check_rels

TEST_ACCOUNT_ID = '000000000000'
TEST_REGION = 'us-east-1'
TEST_UPDATE_TAG = 123456789


def test_load_emr_clusters_nodes(neo4j_session):
    # Act
    data = tests.data.aws.emr.DESCRIBE_CLUSTERS
    cartography.intel.aws.emr.load_emr_clusters(
        neo4j_session,
        data,
        TEST_REGION,
        TEST_ACCOUNT_ID,
        TEST_UPDATE_TAG,
    )

    # Assert
    expected_nodes = {
        ("arn:aws:elasticmapreduce:us-east-1:190000000000:cluster/j-awesome",),
        ("arn:aws:elasticmapreduce:us-east-1:190000000000:cluster/j-meh",),
    }
    assert check_nodes(neo4j_session, 'EMRCluster', ['arn']) == expected_nodes


def test_load_emr_clusters_relationships(neo4j_session):
    # Arrange: Create Test AWSAccount
    neo4j_session.run(
        """
        MERGE (aws:AWSAccount{id: $aws_account_id})
        ON CREATE SET aws.firstseen = timestamp()
        SET aws.lastupdated = $aws_update_tag
        """,
        aws_account_id=TEST_ACCOUNT_ID,
        aws_update_tag=TEST_UPDATE_TAG,
    )

    # Act: Load Test EMR Clusters
    data = tests.data.aws.emr.DESCRIBE_CLUSTERS
    cartography.intel.aws.emr.load_emr_clusters(
        neo4j_session,
        data,
        TEST_REGION,
        TEST_ACCOUNT_ID,
        TEST_UPDATE_TAG,
    )

    # Assert
    expected = {
        (TEST_ACCOUNT_ID, 'arn:aws:elasticmapreduce:us-east-1:190000000000:cluster/j-awesome'),
        (TEST_ACCOUNT_ID, 'arn:aws:elasticmapreduce:us-east-1:190000000000:cluster/j-meh'),
    }
    assert check_rels(
        neo4j_session,
        'AWSAccount',
        'id',
        'EMRCluster',
        'arn',
        'RESOURCE',
    ) == expected
