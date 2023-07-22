# Generated by Django 4.2.3 on 2023-07-07 18:33

from django.db import migrations


def forward(apps, schema_editor):
    """Track any RFCs that were created from tracked drafts"""
    CommunityList = apps.get_model("community", "CommunityList")
    RelatedDocument = apps.get_model("doc", "RelatedDocument")

    # Handle individually tracked documents
    for cl in CommunityList.objects.all():
        for rfc in set(
            RelatedDocument.objects.filter(
                source__in=cl.added_docs.all(),
                relationship__slug="became_rfc",
            ).values_list("target__docs", flat=True)
        ):
            cl.added_docs.add(rfc)

    # Handle rules - rules ending with _rfc should no longer filter by state.
    # There are 9 CommunityLists with invalid author_rfc rules that are filtering
    # by (draft, active) instead of (draft, rfc) state before migration. All but one
    # also includes an author rule for (draft, active), so these will start following
    # RFCs as well. The one exception will start tracking RFCs instead of I-Ds, which
    # is probably what was intended, but will be a change in their user experience.
    SearchRule = apps.get_model("community", "SearchRule")
    rfc_rules = SearchRule.objects.filter(rule_type__endswith="_rfc")
    rfc_rules.update(state=None)

def reverse(apps, schema_editor):
    Document = apps.get_model("doc", "Document")
    for rfc in Document.objects.filter(type__slug="rfc"):
        rfc.communitylist_set.clear()

    # See the comment above regarding author_rfc
    SearchRule = apps.get_model("community", "SearchRule")
    State = apps.get_model("doc", "State")
    SearchRule.objects.filter(rule_type__endswith="_rfc").update(
        state=State.objects.get(type_id="draft", slug="rfc")
    )


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0002_auto_20230320_1222"),
        ("doc", "0010_move_rfc_docaliases"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
