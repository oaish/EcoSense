--
-- PostgreSQL database dump
--

\restrict wrtuwjE08h4bsIdMLnYWaOnjl94EhaOUvb0FPxUq1CKcYDD9U10qwFnhJXZ7JJw

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE ecosense;
--
-- Name: ecosense; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE ecosense WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United Kingdom.1252';


ALTER DATABASE ecosense OWNER TO postgres;

\unrestrict wrtuwjE08h4bsIdMLnYWaOnjl94EhaOUvb0FPxUq1CKcYDD9U10qwFnhJXZ7JJw
\connect ecosense
\restrict wrtuwjE08h4bsIdMLnYWaOnjl94EhaOUvb0FPxUq1CKcYDD9U10qwFnhJXZ7JJw

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bin_fill_readings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bin_fill_readings (
    reading_id bigint NOT NULL,
    bin_id uuid NOT NULL,
    fill_percentage numeric(5,2) NOT NULL,
    recorded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    source character varying(30) DEFAULT 'MANUAL'::character varying NOT NULL,
    notes text,
    CONSTRAINT valid_fill_percentage CHECK (((fill_percentage >= (0)::numeric) AND (fill_percentage <= (100)::numeric)))
);


ALTER TABLE public.bin_fill_readings OWNER TO postgres;

--
-- Name: bin_fill_readings_reading_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bin_fill_readings_reading_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bin_fill_readings_reading_id_seq OWNER TO postgres;

--
-- Name: bin_fill_readings_reading_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bin_fill_readings_reading_id_seq OWNED BY public.bin_fill_readings.reading_id;


--
-- Name: bins; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bins (
    bin_id uuid DEFAULT gen_random_uuid() NOT NULL,
    bin_code character varying(50) NOT NULL,
    location_id bigint NOT NULL,
    waste_type_id smallint NOT NULL,
    capacity_litres numeric(8,2),
    qr_token uuid DEFAULT gen_random_uuid() NOT NULL,
    current_fill_percentage numeric(5,2),
    status character varying(30) DEFAULT 'ACTIVE'::character varying NOT NULL,
    installed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT valid_bin_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'FULL'::character varying, 'DAMAGED'::character varying, 'MISSING'::character varying, 'INACTIVE'::character varying])::text[]))),
    CONSTRAINT valid_fill_percentage CHECK (((current_fill_percentage IS NULL) OR ((current_fill_percentage >= (0)::numeric) AND (current_fill_percentage <= (100)::numeric))))
);


ALTER TABLE public.bins OWNER TO postgres;

--
-- Name: collection_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_records (
    collection_id bigint NOT NULL,
    bin_id uuid NOT NULL,
    collector_id uuid NOT NULL,
    fill_level_before numeric(5,2),
    collected_quantity_kg numeric(8,3),
    fill_level_after numeric(5,2),
    collected_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    notes text,
    CONSTRAINT positive_collected_quantity CHECK (((collected_quantity_kg IS NULL) OR (collected_quantity_kg > (0)::numeric))),
    CONSTRAINT valid_fill_after CHECK (((fill_level_after IS NULL) OR ((fill_level_after >= (0)::numeric) AND (fill_level_after <= (100)::numeric)))),
    CONSTRAINT valid_fill_before CHECK (((fill_level_before IS NULL) OR ((fill_level_before >= (0)::numeric) AND (fill_level_before <= (100)::numeric))))
);


ALTER TABLE public.collection_records OWNER TO postgres;

--
-- Name: collection_records_collection_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collection_records_collection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.collection_records_collection_id_seq OWNER TO postgres;

--
-- Name: collection_records_collection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collection_records_collection_id_seq OWNED BY public.collection_records.collection_id;


--
-- Name: composting_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.composting_records (
    composting_id bigint NOT NULL,
    waste_type_id smallint NOT NULL,
    input_quantity_kg numeric(10,3) NOT NULL,
    output_quantity_kg numeric(10,3),
    composting_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    composting_method character varying(100),
    notes text,
    recorded_by uuid NOT NULL,
    CONSTRAINT positive_input_quantity CHECK ((input_quantity_kg > (0)::numeric)),
    CONSTRAINT valid_output_quantity CHECK (((output_quantity_kg IS NULL) OR (output_quantity_kg >= (0)::numeric)))
);


ALTER TABLE public.composting_records OWNER TO postgres;

--
-- Name: composting_records_composting_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.composting_records_composting_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.composting_records_composting_id_seq OWNER TO postgres;

--
-- Name: composting_records_composting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.composting_records_composting_id_seq OWNED BY public.composting_records.composting_id;


--
-- Name: disposal_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.disposal_records (
    disposal_id bigint NOT NULL,
    user_id uuid NOT NULL,
    bin_id uuid NOT NULL,
    quantity_kg numeric(8,3),
    recorded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    notes text,
    CONSTRAINT positive_disposal_quantity CHECK (((quantity_kg IS NULL) OR (quantity_kg > (0)::numeric)))
);


ALTER TABLE public.disposal_records OWNER TO postgres;

--
-- Name: disposal_records_disposal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.disposal_records_disposal_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.disposal_records_disposal_id_seq OWNER TO postgres;

--
-- Name: disposal_records_disposal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.disposal_records_disposal_id_seq OWNED BY public.disposal_records.disposal_id;


--
-- Name: fill_predictions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fill_predictions (
    prediction_id bigint NOT NULL,
    bin_id uuid NOT NULL,
    predicted_fill_percentage numeric(5,2) NOT NULL,
    prediction_horizon_hours numeric(6,2) NOT NULL,
    predicted_for timestamp with time zone NOT NULL,
    model_version character varying(50),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT positive_prediction_horizon CHECK ((prediction_horizon_hours > (0)::numeric)),
    CONSTRAINT valid_predicted_fill CHECK (((predicted_fill_percentage >= (0)::numeric) AND (predicted_fill_percentage <= (100)::numeric)))
);


ALTER TABLE public.fill_predictions OWNER TO postgres;

--
-- Name: fill_predictions_prediction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fill_predictions_prediction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fill_predictions_prediction_id_seq OWNER TO postgres;

--
-- Name: fill_predictions_prediction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fill_predictions_prediction_id_seq OWNED BY public.fill_predictions.prediction_id;


--
-- Name: gamification_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gamification_actions (
    action_id smallint NOT NULL,
    action_code character varying(50) NOT NULL,
    action_name character varying(100) NOT NULL,
    description text,
    default_points integer NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT valid_default_points CHECK ((default_points >= 0))
);


ALTER TABLE public.gamification_actions OWNER TO postgres;

--
-- Name: gamification_actions_action_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gamification_actions_action_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gamification_actions_action_id_seq OWNER TO postgres;

--
-- Name: gamification_actions_action_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gamification_actions_action_id_seq OWNED BY public.gamification_actions.action_id;


--
-- Name: locations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.locations (
    location_id bigint NOT NULL,
    name character varying(150) NOT NULL,
    location_type character varying(50) NOT NULL,
    building character varying(100),
    floor character varying(30),
    latitude numeric(9,6),
    longitude numeric(9,6),
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.locations OWNER TO postgres;

--
-- Name: locations_location_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.locations_location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.locations_location_id_seq OWNER TO postgres;

--
-- Name: locations_location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.locations_location_id_seq OWNED BY public.locations.location_id;


--
-- Name: recycling_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recycling_records (
    recycling_id bigint NOT NULL,
    waste_type_id smallint NOT NULL,
    quantity_kg numeric(10,3) NOT NULL,
    recycling_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    recycler_name character varying(150),
    reference_number character varying(100),
    notes text,
    recorded_by uuid NOT NULL,
    CONSTRAINT positive_recycling_quantity CHECK ((quantity_kg > (0)::numeric))
);


ALTER TABLE public.recycling_records OWNER TO postgres;

--
-- Name: recycling_records_recycling_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recycling_records_recycling_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recycling_records_recycling_id_seq OWNER TO postgres;

--
-- Name: recycling_records_recycling_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recycling_records_recycling_id_seq OWNED BY public.recycling_records.recycling_id;


--
-- Name: reward_redemptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reward_redemptions (
    redemption_id bigint NOT NULL,
    user_id uuid NOT NULL,
    reward_id bigint NOT NULL,
    points_spent integer NOT NULL,
    status character varying(30) DEFAULT 'PENDING'::character varying NOT NULL,
    redeemed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    processed_at timestamp with time zone,
    processed_by uuid,
    CONSTRAINT positive_points_spent CHECK ((points_spent > 0)),
    CONSTRAINT valid_redemption_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'APPROVED'::character varying, 'REJECTED'::character varying, 'COMPLETED'::character varying])::text[])))
);


ALTER TABLE public.reward_redemptions OWNER TO postgres;

--
-- Name: reward_redemptions_redemption_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reward_redemptions_redemption_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reward_redemptions_redemption_id_seq OWNER TO postgres;

--
-- Name: reward_redemptions_redemption_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reward_redemptions_redemption_id_seq OWNED BY public.reward_redemptions.redemption_id;


--
-- Name: rewards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rewards (
    reward_id bigint NOT NULL,
    reward_name character varying(150) NOT NULL,
    description text,
    points_required integer NOT NULL,
    stock_quantity integer,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT valid_points_required CHECK ((points_required > 0)),
    CONSTRAINT valid_stock_quantity CHECK (((stock_quantity IS NULL) OR (stock_quantity >= 0)))
);


ALTER TABLE public.rewards OWNER TO postgres;

--
-- Name: rewards_reward_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rewards_reward_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rewards_reward_id_seq OWNER TO postgres;

--
-- Name: rewards_reward_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rewards_reward_id_seq OWNED BY public.rewards.reward_id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    role_id smallint NOT NULL,
    role_name character varying(30) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_role_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_role_id_seq OWNER TO postgres;

--
-- Name: roles_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_role_id_seq OWNED BY public.roles.role_id;


--
-- Name: user_points; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_points (
    points_id bigint NOT NULL,
    user_id uuid NOT NULL,
    action_id smallint NOT NULL,
    points integer NOT NULL,
    reference_id bigint,
    description text,
    earned_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT valid_points CHECK ((points > 0))
);


ALTER TABLE public.user_points OWNER TO postgres;

--
-- Name: user_points_points_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_points_points_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_points_points_id_seq OWNER TO postgres;

--
-- Name: user_points_points_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_points_points_id_seq OWNED BY public.user_points.points_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id uuid DEFAULT gen_random_uuid() NOT NULL,
    role_id smallint NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: waste_classifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.waste_classifications (
    classification_id bigint NOT NULL,
    user_id uuid,
    image_url text NOT NULL,
    predicted_waste_type_id smallint,
    confidence_score numeric(5,4),
    model_version character varying(50),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    disposal_id bigint,
    CONSTRAINT valid_confidence_score CHECK (((confidence_score IS NULL) OR ((confidence_score >= (0)::numeric) AND (confidence_score <= (1)::numeric))))
);


ALTER TABLE public.waste_classifications OWNER TO postgres;

--
-- Name: waste_classifications_classification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.waste_classifications_classification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.waste_classifications_classification_id_seq OWNER TO postgres;

--
-- Name: waste_classifications_classification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.waste_classifications_classification_id_seq OWNED BY public.waste_classifications.classification_id;


--
-- Name: waste_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.waste_reports (
    report_id bigint NOT NULL,
    user_id uuid NOT NULL,
    bin_id uuid,
    report_type character varying(50) NOT NULL,
    description text,
    image_url text,
    status character varying(30) DEFAULT 'PENDING'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved_at timestamp with time zone,
    resolved_by uuid,
    CONSTRAINT valid_report_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'IN_PROGRESS'::character varying, 'RESOLVED'::character varying, 'REJECTED'::character varying])::text[])))
);


ALTER TABLE public.waste_reports OWNER TO postgres;

--
-- Name: waste_reports_report_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.waste_reports_report_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.waste_reports_report_id_seq OWNER TO postgres;

--
-- Name: waste_reports_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.waste_reports_report_id_seq OWNED BY public.waste_reports.report_id;


--
-- Name: waste_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.waste_types (
    waste_type_id smallint NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.waste_types OWNER TO postgres;

--
-- Name: waste_types_waste_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.waste_types_waste_type_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.waste_types_waste_type_id_seq OWNER TO postgres;

--
-- Name: waste_types_waste_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.waste_types_waste_type_id_seq OWNED BY public.waste_types.waste_type_id;


--
-- Name: bin_fill_readings reading_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bin_fill_readings ALTER COLUMN reading_id SET DEFAULT nextval('public.bin_fill_readings_reading_id_seq'::regclass);


--
-- Name: collection_records collection_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_records ALTER COLUMN collection_id SET DEFAULT nextval('public.collection_records_collection_id_seq'::regclass);


--
-- Name: composting_records composting_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.composting_records ALTER COLUMN composting_id SET DEFAULT nextval('public.composting_records_composting_id_seq'::regclass);


--
-- Name: disposal_records disposal_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disposal_records ALTER COLUMN disposal_id SET DEFAULT nextval('public.disposal_records_disposal_id_seq'::regclass);


--
-- Name: fill_predictions prediction_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fill_predictions ALTER COLUMN prediction_id SET DEFAULT nextval('public.fill_predictions_prediction_id_seq'::regclass);


--
-- Name: gamification_actions action_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gamification_actions ALTER COLUMN action_id SET DEFAULT nextval('public.gamification_actions_action_id_seq'::regclass);


--
-- Name: locations location_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations ALTER COLUMN location_id SET DEFAULT nextval('public.locations_location_id_seq'::regclass);


--
-- Name: recycling_records recycling_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recycling_records ALTER COLUMN recycling_id SET DEFAULT nextval('public.recycling_records_recycling_id_seq'::regclass);


--
-- Name: reward_redemptions redemption_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reward_redemptions ALTER COLUMN redemption_id SET DEFAULT nextval('public.reward_redemptions_redemption_id_seq'::regclass);


--
-- Name: rewards reward_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rewards ALTER COLUMN reward_id SET DEFAULT nextval('public.rewards_reward_id_seq'::regclass);


--
-- Name: roles role_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN role_id SET DEFAULT nextval('public.roles_role_id_seq'::regclass);


--
-- Name: user_points points_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_points ALTER COLUMN points_id SET DEFAULT nextval('public.user_points_points_id_seq'::regclass);


--
-- Name: waste_classifications classification_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_classifications ALTER COLUMN classification_id SET DEFAULT nextval('public.waste_classifications_classification_id_seq'::regclass);


--
-- Name: waste_reports report_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_reports ALTER COLUMN report_id SET DEFAULT nextval('public.waste_reports_report_id_seq'::regclass);


--
-- Name: waste_types waste_type_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_types ALTER COLUMN waste_type_id SET DEFAULT nextval('public.waste_types_waste_type_id_seq'::regclass);


--
-- Data for Name: bin_fill_readings; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: bins; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: collection_records; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: composting_records; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: disposal_records; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: fill_predictions; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: gamification_actions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.gamification_actions (action_id, action_code, action_name, description, default_points, is_active) VALUES (1, 'DISPOSAL_RECORDED', 'Record Waste Disposal', 'Record a waste disposal using a bin QR code', 5, true);
INSERT INTO public.gamification_actions (action_id, action_code, action_name, description, default_points, is_active) VALUES (2, 'WASTE_REPORT', 'Report Waste Issue', 'Report an overflowing, damaged, or missing bin', 10, true);
INSERT INTO public.gamification_actions (action_id, action_code, action_name, description, default_points, is_active) VALUES (3, 'CORRECT_SEGREGATION', 'Correct Waste Segregation', 'Successfully dispose waste into the appropriate bin', 10, true);
INSERT INTO public.gamification_actions (action_id, action_code, action_name, description, default_points, is_active) VALUES (4, 'CAMPAIGN_PARTICIPATION', 'Campaign Participation', 'Participate in a campus sustainability campaign', 20, true);


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: recycling_records; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: reward_redemptions; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: rewards; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.roles (role_id, role_name) VALUES (1, 'STUDENT');
INSERT INTO public.roles (role_id, role_name) VALUES (2, 'STAFF');
INSERT INTO public.roles (role_id, role_name) VALUES (3, 'COLLECTOR');
INSERT INTO public.roles (role_id, role_name) VALUES (4, 'ADMIN');


--
-- Data for Name: user_points; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: waste_classifications; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: waste_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: waste_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.waste_types (waste_type_id, name, description, is_active) VALUES (1, 'WET_ORGANIC', 'Organic and wet waste', true);
INSERT INTO public.waste_types (waste_type_id, name, description, is_active) VALUES (2, 'DRY_RECYCLABLE', 'Dry recyclable waste', true);
INSERT INTO public.waste_types (waste_type_id, name, description, is_active) VALUES (3, 'PAPER', 'Paper waste', true);
INSERT INTO public.waste_types (waste_type_id, name, description, is_active) VALUES (4, 'METAL', 'Metal waste', true);
INSERT INTO public.waste_types (waste_type_id, name, description, is_active) VALUES (5, 'E_WASTE', 'Electronic waste', true);
INSERT INTO public.waste_types (waste_type_id, name, description, is_active) VALUES (6, 'GARDEN', 'Garden and landscaping waste', true);


--
-- Name: bin_fill_readings_reading_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bin_fill_readings_reading_id_seq', 1, false);


--
-- Name: collection_records_collection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.collection_records_collection_id_seq', 1, false);


--
-- Name: composting_records_composting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.composting_records_composting_id_seq', 1, false);


--
-- Name: disposal_records_disposal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.disposal_records_disposal_id_seq', 1, false);


--
-- Name: fill_predictions_prediction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fill_predictions_prediction_id_seq', 1, false);


--
-- Name: gamification_actions_action_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gamification_actions_action_id_seq', 4, true);


--
-- Name: locations_location_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.locations_location_id_seq', 1, false);


--
-- Name: recycling_records_recycling_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recycling_records_recycling_id_seq', 1, false);


--
-- Name: reward_redemptions_redemption_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reward_redemptions_redemption_id_seq', 1, false);


--
-- Name: rewards_reward_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rewards_reward_id_seq', 1, false);


--
-- Name: roles_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_role_id_seq', 4, true);


--
-- Name: user_points_points_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_points_points_id_seq', 1, false);


--
-- Name: waste_classifications_classification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.waste_classifications_classification_id_seq', 1, false);


--
-- Name: waste_reports_report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.waste_reports_report_id_seq', 1, false);


--
-- Name: waste_types_waste_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.waste_types_waste_type_id_seq', 6, true);


--
-- Name: bin_fill_readings bin_fill_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bin_fill_readings
    ADD CONSTRAINT bin_fill_readings_pkey PRIMARY KEY (reading_id);


--
-- Name: bins bins_bin_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bins
    ADD CONSTRAINT bins_bin_code_key UNIQUE (bin_code);


--
-- Name: bins bins_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bins
    ADD CONSTRAINT bins_pkey PRIMARY KEY (bin_id);


--
-- Name: bins bins_qr_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bins
    ADD CONSTRAINT bins_qr_token_key UNIQUE (qr_token);


--
-- Name: collection_records collection_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_records
    ADD CONSTRAINT collection_records_pkey PRIMARY KEY (collection_id);


--
-- Name: composting_records composting_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.composting_records
    ADD CONSTRAINT composting_records_pkey PRIMARY KEY (composting_id);


--
-- Name: disposal_records disposal_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disposal_records
    ADD CONSTRAINT disposal_records_pkey PRIMARY KEY (disposal_id);


--
-- Name: fill_predictions fill_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fill_predictions
    ADD CONSTRAINT fill_predictions_pkey PRIMARY KEY (prediction_id);


--
-- Name: gamification_actions gamification_actions_action_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gamification_actions
    ADD CONSTRAINT gamification_actions_action_code_key UNIQUE (action_code);


--
-- Name: gamification_actions gamification_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gamification_actions
    ADD CONSTRAINT gamification_actions_pkey PRIMARY KEY (action_id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (location_id);


--
-- Name: recycling_records recycling_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recycling_records
    ADD CONSTRAINT recycling_records_pkey PRIMARY KEY (recycling_id);


--
-- Name: reward_redemptions reward_redemptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reward_redemptions
    ADD CONSTRAINT reward_redemptions_pkey PRIMARY KEY (redemption_id);


--
-- Name: rewards rewards_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rewards
    ADD CONSTRAINT rewards_pkey PRIMARY KEY (reward_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);


--
-- Name: roles roles_role_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_role_name_key UNIQUE (role_name);


--
-- Name: user_points user_points_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_points
    ADD CONSTRAINT user_points_pkey PRIMARY KEY (points_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: waste_classifications waste_classifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_classifications
    ADD CONSTRAINT waste_classifications_pkey PRIMARY KEY (classification_id);


--
-- Name: waste_reports waste_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_reports
    ADD CONSTRAINT waste_reports_pkey PRIMARY KEY (report_id);


--
-- Name: waste_types waste_types_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_types
    ADD CONSTRAINT waste_types_name_key UNIQUE (name);


--
-- Name: waste_types waste_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_types
    ADD CONSTRAINT waste_types_pkey PRIMARY KEY (waste_type_id);


--
-- Name: bin_fill_readings bin_fill_readings_bin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bin_fill_readings
    ADD CONSTRAINT bin_fill_readings_bin_id_fkey FOREIGN KEY (bin_id) REFERENCES public.bins(bin_id);


--
-- Name: bins bins_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bins
    ADD CONSTRAINT bins_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(location_id);


--
-- Name: bins bins_waste_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bins
    ADD CONSTRAINT bins_waste_type_id_fkey FOREIGN KEY (waste_type_id) REFERENCES public.waste_types(waste_type_id);


--
-- Name: collection_records collection_records_bin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_records
    ADD CONSTRAINT collection_records_bin_id_fkey FOREIGN KEY (bin_id) REFERENCES public.bins(bin_id);


--
-- Name: collection_records collection_records_collector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_records
    ADD CONSTRAINT collection_records_collector_id_fkey FOREIGN KEY (collector_id) REFERENCES public.users(user_id);


--
-- Name: composting_records composting_records_recorded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.composting_records
    ADD CONSTRAINT composting_records_recorded_by_fkey FOREIGN KEY (recorded_by) REFERENCES public.users(user_id);


--
-- Name: composting_records composting_records_waste_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.composting_records
    ADD CONSTRAINT composting_records_waste_type_id_fkey FOREIGN KEY (waste_type_id) REFERENCES public.waste_types(waste_type_id);


--
-- Name: disposal_records disposal_records_bin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disposal_records
    ADD CONSTRAINT disposal_records_bin_id_fkey FOREIGN KEY (bin_id) REFERENCES public.bins(bin_id);


--
-- Name: disposal_records disposal_records_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disposal_records
    ADD CONSTRAINT disposal_records_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: fill_predictions fill_predictions_bin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fill_predictions
    ADD CONSTRAINT fill_predictions_bin_id_fkey FOREIGN KEY (bin_id) REFERENCES public.bins(bin_id);


--
-- Name: recycling_records recycling_records_recorded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recycling_records
    ADD CONSTRAINT recycling_records_recorded_by_fkey FOREIGN KEY (recorded_by) REFERENCES public.users(user_id);


--
-- Name: recycling_records recycling_records_waste_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recycling_records
    ADD CONSTRAINT recycling_records_waste_type_id_fkey FOREIGN KEY (waste_type_id) REFERENCES public.waste_types(waste_type_id);


--
-- Name: reward_redemptions reward_redemptions_processed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reward_redemptions
    ADD CONSTRAINT reward_redemptions_processed_by_fkey FOREIGN KEY (processed_by) REFERENCES public.users(user_id);


--
-- Name: reward_redemptions reward_redemptions_reward_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reward_redemptions
    ADD CONSTRAINT reward_redemptions_reward_id_fkey FOREIGN KEY (reward_id) REFERENCES public.rewards(reward_id);


--
-- Name: reward_redemptions reward_redemptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reward_redemptions
    ADD CONSTRAINT reward_redemptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: user_points user_points_action_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_points
    ADD CONSTRAINT user_points_action_id_fkey FOREIGN KEY (action_id) REFERENCES public.gamification_actions(action_id);


--
-- Name: user_points user_points_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_points
    ADD CONSTRAINT user_points_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(role_id);


--
-- Name: waste_classifications waste_classifications_disposal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_classifications
    ADD CONSTRAINT waste_classifications_disposal_id_fkey FOREIGN KEY (disposal_id) REFERENCES public.disposal_records(disposal_id);


--
-- Name: waste_classifications waste_classifications_predicted_waste_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_classifications
    ADD CONSTRAINT waste_classifications_predicted_waste_type_id_fkey FOREIGN KEY (predicted_waste_type_id) REFERENCES public.waste_types(waste_type_id);


--
-- Name: waste_classifications waste_classifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_classifications
    ADD CONSTRAINT waste_classifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: waste_reports waste_reports_bin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_reports
    ADD CONSTRAINT waste_reports_bin_id_fkey FOREIGN KEY (bin_id) REFERENCES public.bins(bin_id);


--
-- Name: waste_reports waste_reports_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_reports
    ADD CONSTRAINT waste_reports_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(user_id);


--
-- Name: waste_reports waste_reports_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waste_reports
    ADD CONSTRAINT waste_reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- PostgreSQL database dump complete
--

\unrestrict wrtuwjE08h4bsIdMLnYWaOnjl94EhaOUvb0FPxUq1CKcYDD9U10qwFnhJXZ7JJw

