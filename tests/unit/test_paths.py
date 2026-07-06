from quantlab.utils.paths import PROJECT_ROOT, project_path


def test_project_root_exists():
    assert PROJECT_ROOT.exists()


def test_project_path_points_inside_project():
    assert project_path("configs", "base.yaml").exists()
