import pandas as pd
import bolo

from lib import events
from lib.columns import rearrange_allegation_columns, rearrange_event_columns
from lib.personnel import fuse_personnel


def fuse_events(cprr, pprr):
    builder = events.Builder()
    builder.extract_events(
        cprr,
        {
            events.COMPLAINT_RECEIVE: {
                "prefix": "receive",
                "keep": ["uid", "agency", "allegation_uid"],
            },
            events.INVESTIGATION_COMPLETE: {
                "prefix": "investigation_complete",
                "keep": ["uid", "agency", "allegation_uid"],
            },
        },
        ["uid", "allegation_uid"],
    )
    builder.extract_events(
        pprr,
        {
            events.OFFICER_HIRE: {
                "prefix": "hire",
                "keep": ["uid", "agency", "rank_desc"],
            },
            events.OFFICER_LEFT: {
                "prefix": "left",
                "keep": ["uid", "agency", "rank_desc", "left_reason"],
            },
        },
        ["uid"],
    )
    return builder.to_frame()


if __name__ == "__main__":
    cprr = pd.read_csv(bolo.data("clean/cprr_rayne_pd_2019_2020.csv"))
    pprr = pd.read_csv(bolo.data("clean/pprr_rayne_pd_2010_2020.csv"))
    post_event = pd.read_csv(bolo.data("match/post_event_rayne_pd_2020_11_06.csv"))
    per = fuse_personnel(cprr, pprr)
    com = rearrange_allegation_columns(cprr)
    events_df = rearrange_event_columns(
        pd.concat([post_event, fuse_events(cprr, pprr)])
    )
    per.to_csv(bolo.data("fuse/per_rayne_pd.csv"), index=False)
    com.to_csv(bolo.data("fuse/com_rayne_pd.csv"), index=False)
    events_df.to_csv(bolo.data("fuse/event_rayne_pd.csv"), index=False)